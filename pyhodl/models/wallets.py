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


""" Wallets-related models """

from bisect import bisect
from datetime import datetime

import numpy as np

from pyhodl.apis.prices.utils import get_price_on_date
from pyhodl.config import VALUE_KEY, DATE_TIME_KEY
from pyhodl.data.tables import get_coin_prices_table
from pyhodl.utils.dak import is_crypto, is_nan


class Wallet:
    """ A general wallet, tracking addition, deletions and fees """

    def __init__(self, base_currency):
        self.base_currency = base_currency  # todo use Coin()
        self.transactions = []  # list of operations performed
        self.is_sorted = False

    def is_crypto(self):
        """
        :return: bool
            True iff wallet base currency is crypto currency
        """

        return is_crypto(self.base_currency)

    def _sort_transactions(self):
        """
        :return: void
            Sort transactions by date
        """

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
        self.is_sorted = False

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
        if subtotals:
            total = subtotals[-1][VALUE_KEY]  # amount of coins

            if now:  # convert to currency now
                price = get_price_on_date(
                    [self.base_currency], currency, datetime.now(), tor=False
                )[self.base_currency]
                return float(price) * total

            if currency:  # convert to currency
                return self.convert_to(
                    subtotals[-1]["transaction"].date,
                    currency,
                    amount=total
                )

            return total
        return 0.0

    def convert_to(self, date_time, currency, amount=1.0):
        """
        :param date_time: datetime
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
            val = prices_table.get_value_on(self.base_currency, date_time)
            return float(val) * amount
        except:
            return 0.0

    def get_price_on(self, dates, currency):
        """
        :param dates: [] of datetime
            List of dates
        :param currency: str
            Currency to get price
        :return: [] of float
            List of prices if coin converted to currency on those dates
        """

        return [
            self.convert_to(date, currency) for date in dates
        ]

    def get_delta_by_transaction(self):
        """
        :return: [] of {}
            List of delta balance by transaction
        """

        self._sort_transactions()
        data = []
        for transaction in self.transactions:
            delta = transaction.get_amount(self.base_currency)
            if delta != 0.0:  # balance has actually changed
                data.append({
                    "transaction": transaction,
                    VALUE_KEY: delta
                })
        return data

    def get_data_by_date(self, data, dates, currency=None):
        """
        :param data: str
            Data to get. Must be in ["delta", "balance"]
        :param dates: [] of datetime
            List of dates
        :param currency: str or None
            Currency to convert deltas to
        :return: [] of {}
            List of delta amount by date
        """

        if data == "delta":
            data = self.get_delta_by_transaction(), dates, currency
        elif data == "balance":
            data = self.get_balance_by_transaction()
        else:
            raise ValueError(data + "not available")

        return self.fill_missing_transactions(data, dates, currency)

    def get_balance_by_transaction(self):
        """
        :return: [] of {}
            List of balance by transaction
        """

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

    def get_balance_array_by_date(self, dates, currency=None):
        """
        :param dates: [] of datetime
            List of dates
        :param currency: str or None
            Currency to convert balances to
        :return: numpy array
            Balance value by date
        """

        balances = self.get_data_by_date("balance", dates, currency)
        lst = np.zeros(len(balances))
        for i, balance in enumerate(balances):
            if not is_nan(balance):
                lst[i] += balance
        return lst

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

    def fill_missing_transactions(self, data, dates, currency=None):
        """
        :param data: [] of {}
            List of transactions
        :param dates: [] of datetime
            All dates
        :param currency: str or None
            Currency to convert balances to
        :return: [] of {}
            Fill missing data: when date not in original data, we create a
            new data point with value the last value
        """

        filled = self.fill_missing_data(
            [transaction[VALUE_KEY] for transaction in data],  # data
            [transaction["transaction"].date for transaction in data],  # dates
            dates
        )

        if currency:
            filled = [
                self.convert_to(
                    data[DATE_TIME_KEY],
                    currency,
                    float(data[VALUE_KEY])
                )
                for data in filled
            ]

        return filled
