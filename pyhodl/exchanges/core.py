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


""" Analyze transactions in exchanges """

import abc
from datetime import timedelta

import matplotlib.pylab as plt

from pyhodl.utils import generate_dates, get_full_lists


class CryptoExchange(object):
    """ Exchange dealing with crypto-coins """

    balance_intervals = {
        "1h": 1,
        "1d": 24,
        "7d": 24 * 7,
        "30d": 24 * 30,
        "3m": 24 * 30 * 3,
        "6m": 24 * 30 * 6,
        "1y": 24 * 365
    }  # interval -> hours

    def __init__(self, transactions):
        """
        :param transactions: [] of Transaction
            List of transactions
        """

        object.__init__(self)
        self.transactions = transactions
        if not self.transactions:
            raise ValueError("Creating exchange with no past transaction!")

    def get_transactions_count(self):
        """
        :return: int
            Number of transactions
        """

        return len(self.transactions)

    def get_first_transaction(self):
        """
        :return: Transaction
            First transaction done (with respect to time)
        """

        first = self.transactions[0]
        for transaction in self.transactions:
            if transaction.date < first.date:
                first = transaction
        return first

    def get_last_transaction(self):
        """
        :return: Transaction
            Last transaction done (with respect to time)
        """

        last = self.transactions[0]
        for transaction in self.transactions:
            if transaction.date > last.date:
                last = transaction
        return last

    def get_transactions(self, since, until):
        """
        :param since: datetime
            Get transactions done since this date (included)
        :param until: datetime
            Get transactions done until this date (excluded)
        :return: (generator of) [] of Transaction
            List of transactions done between the dates
        """

        for transaction in self.transactions:
            if since <= transaction.date < until:
                yield transaction

    def get_transactions_with(self, symbol):
        """
        :param symbol: str
            Currency e.g EUR, BTC, LTC ...
        :return: (generator of) [] of Transaction
            List of transactions done with this currency
        """

        for transaction in self.transactions:
            if transaction.has(symbol):
                yield transaction

    @abc.abstractmethod
    def get_balance(self, since, until):
        """
        :param since: datetime
            Get transactions done since this date
        :param until: datetime
            Get transactions done until this date
        :return: Balance
            List of wallets for each coin
        """

        return

    def get_balance_subtotals(self, since, until, interval):
        """
        :param since: datetime
            Get transactions done since this date
        :param until: datetime
            Get transactions done until this date
        :param interval: str
            Interval of times (1h, 1d, 7d, 30d, 3m, 6m, 1y)
        :return: [] of {}
            List of wallets for each coin for each time-frame
        """

        if interval not in self.balance_intervals:
            raise ValueError("Interval must be one of ",
                             self.balance_intervals.keys())

        dates_list = list(
            generate_dates(
                since, until + timedelta(seconds=1),  # add little margin
                self.balance_intervals[interval]
            )
        )

        wallet_list = []
        for i, date in enumerate(dates_list[:-1]):
            date_min = date
            date_max = dates_list[i + 1]
            date_balances = self.get_balance(date_min, date_max)
            if wallet_list:  # merge with last
                date_balances.merge(wallet_list[-1]["balance"])

            wallet_list.append(
                {
                    "date": date_max,
                    "balance": date_balances
                }
            )

        return wallet_list

    def plot_balance_subtotals(self, since, until, interval):
        """
        :param since: datetime
            Get transactions done since this date
        :param until: datetime
            Get transactions done until this date
        :param interval: str
            Interval of times (1h, 1d, 7d, 30d, 3m, 6m, 1y)
        :return: void
            Shows plot with subtotals
        """

        subtotals = self.get_balance_subtotals(since, until, interval)
        data = {
            date_balance["date"]: date_balance["balance"].get_balance()
            for date_balance in subtotals
        }
        data = get_full_lists(data)

        plt.grid(True)
        for key, value in data.items():
            sorted_values = sorted(value.items())
            dates = [
                item[0] for item in sorted_values
            ]
            values = [
                float(item[1]) if item[1] else float("nan")
                for item in sorted_values
            ]

            plt.plot(
                dates,
                values,
                label=key
            )  # plot data

        plt.xlabel("Time")
        plt.ylabel("Amount")
        plt.legend()  # build legend
        plt.title("Subtotal cap")
        plt.show()


class Transaction(object):
    """ Exchange transaction """

    def __init__(self, raw_dict, date_key=None):
        """
        :param raw_dict: {}
            Dict containing raw data
        :param date_key: str
            Key to get date info
        """

        object.__init__(self)
        self.raw = raw_dict
        if date_key:
            self.date = self.raw[date_key]
        else:
            self.date = None

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
        return str(self.raw)


class Wallet(object):
    """ A general wallet, tracking addition, deletions and fees """

    def __init__(self, start_amount=0):
        """
        :param start_amount: float
            Amount of currency at start
        """

        object.__init__(self)
        self.balance = float(0)
        self.transactions = []  # list of operations performed

        if start_amount > 0:
            self.add(start_amount)
        elif start_amount < 0:
            self.remove(start_amount)

    def add(self, amount):
        """
        :param amount: float
            Amount to be added to balance
        :return: void
            Adds amount to balance
        """

        self.transactions.append(
            Transaction(
                {
                    "action": "add",
                    "amount": amount
                }
            )
        )

        self.balance += amount

    def remove(self, amount):
        """
        :param amount: float
            Amount to be removed to balance
        :return: void
            Removes amount from balance
        """

        self.transactions.append(
            Transaction(
                {
                    "action": "remove",
                    "amount": amount
                }
            )
        )

        self.balance -= float(amount)

    def get_balance(self):
        """
        :return: float
            Current balance
        """

        return self.balance

    def merge(self, other):
        """
        :param other: Wallet
            Other wallet to merge with
        :return: void
            Add other's transactions to this wallet
        """

        for transaction in other.transactions:  # redo same actions
            if transaction["action"] == "add":
                self.add(transaction["amount"])
            else:
                self.remove(transaction["amount"])


class Balance(object):
    """ Balance of something, expressed in many coins """

    def __init__(self, wallets):
        """
        :param wallets: {} of Wallet
            List of wallet (and coins)
        """

        object.__init__(self)
        self.wallets = wallets

    def merge(self, other):
        """
        :param other: Balance
            Other balance to merge with
        :return: void
            Merges other's wallets
        """

        for coin, wallet in other.wallets.items():
            if coin not in self.wallets:  # new coin
                self.wallets[coin] = wallet
            else:  # coin wallet has to be merged
                self.wallets[coin].merge(wallet)

    def get_balance(self):
        """
        :return: {} str -> float
            For each coin, evaluate balance
        """

        return {
            coin: wallet.get_balance() for coin, wallet in self.wallets.items()
        }
