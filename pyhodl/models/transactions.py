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

from enum import Enum


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
        self.date = date
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
        """
        :param create_date: datetime
            Date of transaction
        ::param start_amount: float
            Amount of currency at start
        """

        self.currency = base_currency
        self.transactions = []  # list of operations performed

    def add_transaction(self, transaction):
        """
        :param transaction: Transaction
            Transaction
        :return: void
            Adds amount to balance
        """

        self.transactions.append(transaction)

    def remove(self, amount, date):
        """
        :param amount: float
            Amount to be removed to balance
        :param date: datetime
            Date of transaction
        :return: void
            Removes amount from balance
        """

        self.transactions.append(
            {
                "action": "out",
                "amount": abs(amount),
                "date": date
            }
        )

        self.balance -= abs(amount)

    def dates(self):
        """
        :return: [] of datetime
            List of all dates
        """

        return [
            transaction.date for transaction in self.transactions
        ]

    def balance(self):
        """
        :return: float
            Balance up to date with last transaction
        """

        amount = 0.0
        for transaction in self.transactions:
            print(transaction.date, transaction.transaction_type, amount)
            if transaction.transaction_type == TransactionType.TRADING:
                if transaction.coin_buy == self.currency:
                    amount += transaction.buy_amount
                    print("+", transaction.buy_amount)

                if transaction.coin_sell == self.currency:
                    amount -= transaction.sell_amount
                    print("-", transaction.sell_amount)

                if transaction.commission and transaction.commission.coin \
                        == self.currency:
                    amount -= transaction.commission.amount
                    print("-", transaction.commission.amount)

            if transaction.transaction_type == TransactionType.COMMISSION:
                if transaction.commission.coin == self.currency:
                    amount -= transaction.commission.amount
                    print("-", transaction.commission.amount)

            if transaction.transaction_type == TransactionType.DEPOSIT:
                if transaction.coin_buy == self.currency:
                    amount += transaction.buy_amount
                    print("+", transaction.buy_amount)

            if transaction.transaction_type == TransactionType.WITHDRAWAL:
                if transaction.coin_sell == self.currency:
                    amount -= transaction.sell_amount
                    print("-", transaction.sell_amount)

        return amount
