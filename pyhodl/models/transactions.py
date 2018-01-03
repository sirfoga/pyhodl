# !/usr/bin/python3
# coding: utf_8

# Copyright 2017-2018 Stefano Fogarollo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


""" Core models """

from bisect import bisect
from datetime import datetime
from enum import Enum

import pytz

from pyhodl.apis.prices import get_price
from pyhodl.config import VALUE_KEY, DATE_TIME_KEY
from pyhodl.data.tables import get_coin_prices_table


class TransactionType(Enum):
    """ Deposit, withdrawal ... """

    NULL = 0
    DEPOSIT = 1
    WITHDRAWAL = 2
    TRADING = 3
    FUNDING = 4
    ORDER = 5
    COMMISSION = 6


class Transaction:
    """ Exchange transaction """

    def __init__(self, raw_dict,
                 coin_bought, buy_amount,
                 coin_sold, sell_amount, date,
                 trans_type=TransactionType.TRADING,
                 successful=True, commission=None):
        """
        :param raw_dict: {}
            Dict containing raw data
        :param trans_type: TransactionType
            Type of transactions
        :param date: date
            Date info
        :param successful: bool
            True iff transaction has actually taken place
        :param commission: Transaction
            Commission of transaction (if any)
        """

        self.raw = raw_dict
        self.coin_buy = str(coin_bought)
        self.buy_amount = float(buy_amount) if buy_amount else 0
        self.coin_sell = str(coin_sold)
        self.sell_amount = float(sell_amount) if sell_amount else 0
        self.transaction_type = trans_type
        self.date = pytz.utc.localize(date) if not date.tzinfo else date
        self.successful = bool(successful)
        self.commission = commission

    def get_attrs(self):
        """
        :return: []
            Keys of internal dict
        """

        return list(self.raw.keys())

    def has(self, item):
        """
        :param item: str
            Item to look for
        :return: bool
            True iff item is in any of the data
        """

        for key, value in self.raw.items():
            try:
                if str(item) in str(value) or str(item) in str(key):
                    return True
            except:
                pass
        return False

    def __getitem__(self, key):
        return self.raw[key]

    def __str__(self):
        out = "Transaction on " + str(self.date)
        if self.buy_amount > 0:
            out += "\n+" + str(self.buy_amount) + " " + str(self.coin_buy)

        if self.sell_amount > 0:
            out += "\n-" + str(self.sell_amount) + " " + str(self.coin_sell)

        if self.commission:
            out += "\nPaying " + str(self.commission.amount) + " " + \
                   str(self.commission.coin) + " as fee"
        out += "\nSuccessful? " + str(self.successful)

        return out


class Commission(Transaction):
    """ Transaction commission """

    def __init__(self, raw_dict, coin, amount, date, successful=True):
        """
        :param raw_dict: {}
            Dict containing raw data
        :param date: date
            Date info
        :param successful: bool
            True iff transaction has actually taken place
        """

        Transaction.__init__(
            self,
            raw_dict,
            coin_bought=None,
            buy_amount=None,
            coin_sold=coin,
            sell_amount=amount,
            date=date,
            trans_type=TransactionType.COMMISSION,
            successful=successful
        )

        self.coin = self.coin_sell
        self.amount = self.sell_amount


class Wallet:
    """ A general wallet, tracking addition, deletions and fees """

    def __init__(self, base_currency):
        self.base_currency = base_currency
        self.transactions = []  # list of operations performed
        self.is_sorted = False

    def _sort_transactions(self):
        if not self.is_sorted:
            self.transactions = sorted(
                self.transactions, key=lambda x: x.date
            )  # sort by date
            self.is_sorted = True

    def add_transaction(self, transaction):
        """
        :param transaction: Transaction
            Transaction
        :return: void
            Adds amount to balance
        """

        self.transactions.append(transaction)

    def dates(self):
        """
        :return: [] of datetime
            List of all dates
        """

        self._sort_transactions()
        return [
            transaction.date for transaction in self.transactions
        ]

    def balance(self, currency=None, now=False):
        """
        :return: float
            Balance up to date with last transaction
        """

        subtotals = self.get_balance_by_transaction()
        total = subtotals[-1][VALUE_KEY]  # amount of coins

        if now:  # convert to currency now
            now = datetime.now()
            price = get_price([self.base_currency], now, currency, tor=False)
            return float(price) * total

        if currency:  # convert to currency
            return self.convert_to(
                subtotals[-1].date,
                currency,
                amount=total
            )

        return total

    def convert_to(self, dt, currency, amount=1.0):
        """
        :param dt: datetime
            Date and time of conversion
        :param currency: str
            Currency to convert to
        :param amount: float
            Amount to convert
        :return: float
            Amount of wallet base currency converted to currency
        """

        try:
            prices_table = get_coin_prices_table(currency)
            val = prices_table.get_value_on(self.base_currency, dt)
            return float(val) * amount
        except:
            return 0.0

    def get_delta_by_transaction(self):
        self._sort_transactions()
        data = []
        for transaction in self.transactions:
            delta_balance = 0.0
            has_edited_balance = False  # True iff coin was traded

            if transaction.transaction_type == TransactionType.TRADING:
                if transaction.coin_buy == self.base_currency:
                    delta_balance += transaction.buy_amount
                    has_edited_balance = True

                if transaction.coin_sell == self.base_currency:
                    delta_balance -= transaction.sell_amount
                    has_edited_balance = True

                if transaction.commission and transaction.commission.coin \
                        == self.base_currency:
                    delta_balance -= transaction.commission.amount
                    has_edited_balance = True

            if transaction.transaction_type == TransactionType.COMMISSION:
                if transaction.commission.coin == self.base_currency:
                    delta_balance -= transaction.commission.amount
                    has_edited_balance = True

            if transaction.transaction_type == TransactionType.DEPOSIT:
                if transaction.coin_buy == self.base_currency:
                    delta_balance += transaction.buy_amount
                    has_edited_balance = True

            if transaction.transaction_type == TransactionType.WITHDRAWAL:
                if transaction.coin_sell == self.base_currency:
                    delta_balance -= transaction.sell_amount
                    has_edited_balance = True

            if has_edited_balance:  # balance has changed
                data.append({
                    "transaction": transaction,
                    VALUE_KEY: delta_balance
                })
        return data

    def get_delta_by_date(self, dates):
        deltas = self.get_delta_by_transaction()
        return self.fill_missing_data(
            [data[VALUE_KEY] for data in deltas],  # data
            [data["transaction"].date for data in deltas],  # dates
            dates
        )

    def get_balance_by_transaction(self):
        deltas = self.get_delta_by_transaction()
        if not deltas:
            return []

        balances = [deltas[0]]
        for delta in deltas[1:]:
            balances.append({
                "transaction": delta["transaction"],
                VALUE_KEY: balances[-1][VALUE_KEY] + delta[VALUE_KEY]
            })
        return balances

    def get_balance_by_date(self, dates, currency=None):
        """
        :param dates: [] of datetime
            List of dates
        :param currency: str or None
            Currency to convert balances to
        :return: [] of {}
            List of balance amount by date
        """

        balances = self.get_balance_by_transaction()
        filled = self.fill_missing_data(
            [data[VALUE_KEY] for data in balances],  # data
            [data["transaction"].date for data in balances],  # dates
            dates
        )

        if currency:
            filled = [
                self.convert_to(
                    balance[DATE_TIME_KEY],
                    currency,
                    float(balance[VALUE_KEY])
                )
                for balance in filled
            ]

        return filled

    @staticmethod
    def fill_missing_data(data, dates, all_dates):
        """
        :param data: [] of summable (e.g float)
            Data to be filled
        :param dates: [] of datetime
            Dates of data
        :param all_dates: [] of datetime
            Full dates
        :return: [] of {}
            Fill missing data: when date not in original data, we create a
            new data point with value the last value
        """

        filled = []

        for date in all_dates:
            i = bisect(dates, date)
            if i == 0:
                filled.append({
                    DATE_TIME_KEY: date,
                    VALUE_KEY: 0.0
                })
            elif date in dates:
                filled.append({
                    DATE_TIME_KEY: date,
                    VALUE_KEY: data[i - 1]
                })
            else:
                filled.append(filled[-1])

        return filled
