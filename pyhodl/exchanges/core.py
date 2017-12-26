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
from enum import Enum

import matplotlib.pylab as plt
from hal.files.save_as import write_dicts_to_csv

from pyhodl.requests import get_price
from pyhodl.utils import generate_dates, get_full_lists


class CryptoExchange(object):
    """ Exchange dealing with crypto-coins """

    TIME_INTERVALS = {
        "1h": 1,
        "1d": 24,
        "7d": 24 * 7,
        "30d": 24 * 30,
        "3m": 24 * 30 * 3,
        "6m": 24 * 30 * 6,
        "1y": 24 * 365
    }  # interval -> hours
    OUTPUT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

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

    def get_transactions(self, since, until, including_until=False):
        """
        :param since: datetime
            Get transactions done since this date (included)
        :param until: datetime
            Get transactions done until this date (excluded)
        :param including_until: bool
            True iff you want to include until date in list
        :return: (generator of) [] of Transaction
            List of transactions done between the dates
        """

        for transaction in self.transactions:
            if including_until:
                if since <= transaction.date <= until:
                    yield transaction
            else:
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

        if interval not in self.TIME_INTERVALS:
            raise ValueError("Interval must be one of ",
                             self.TIME_INTERVALS.keys())

        dates_list = list(
            generate_dates(
                since, until,
                self.TIME_INTERVALS[interval]
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

    def plot_balance_subtotals(self, since, until, interval, title):
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
        plt.title(title)
        plt.show()

    def get_all_transactions(self):
        """
        :return: [] of {}
            List of all transactions (all coins)
        """

        wallets = self.get_balance(
            since=self.get_first_transaction().date,
            until=self.get_last_transaction().date + timedelta(seconds=1)
        ).wallets

        wallets = {
            coin: list(wallet.get_transactions_dict())
            for coin, wallet in wallets.items()
        }

        all_transactions = []
        for coin, transactions in wallets.items():
            for i, transaction in enumerate(transactions):
                transactions[i]["coin"] = str(coin)
            all_transactions += transactions

        return sorted(all_transactions, key=lambda k: k["date"])

    def get_all_balances(self):
        """
        :return: [] of {}
            List of all transactions (all coins)
        """

        wallets = self.get_balance(
            since=self.get_first_transaction().date,
            until=self.get_last_transaction().date + timedelta(seconds=1)
        ).wallets

        dates = set()  # dates of all transactions
        coins = set()  # all coins
        for coin, wallet in wallets.items():
            coins.add(coin)
            for transaction in wallet.transactions:
                dates.add(transaction["date"])
        dates = sorted(list(dates))  # sort by date
        coins = sorted(list(coins))  # sort alphabetically

        first = {
            coin: wallets[coin].get_amount(dates[0]) for coin in coins
        }
        first["date"] = dates[0]  # build first
        all_balances = [
            first
        ]

        for date in dates[1:]:
            balance = {
                coin: all_balances[-1][coin] + wallets[coin].get_amount(date)
                for coin in coins
            }
            balance["date"] = date
            all_balances.append(balance)

        return all_balances

    def get_all_balances_equiv(self, currency):
        """
        :param currency: str
            Currency to get price
        :return: void
            Saves all balances to .csv
        """

        data = self.get_all_balances()
        for i, balance in enumerate(data):
            coins = [
                coin for coin in balance if coin.isupper()
            ]
            prices = get_price(coins, currency, balance["date"])
            print("Getting balance of", balance["date"], "...")

            for coin, price in prices.items():
                equiv = balance[coin] * price
                data[i][coin + " (" + currency + " value)"] = equiv
        return data

    def write_all_balances_to_csv(self, out, currency=None):
        """
        :param out: str
            Path to output file
        :param currency: str
            Currency to get price
        :return: void
            Saves all balances to .csv
        """

        if currency is not None:
            data = self.get_all_balances_equiv(currency)
        else:
            data = self.get_all_balances()

        self.write_data_to_csv(data, out)

    def write_all_transactions_to_csv(self, out):
        """
        :param out: str
            Path to output file
        :return: void
            Saves all transactions to .csv
        """

        self.write_data_to_csv(self.get_all_transactions(), out)

    @staticmethod
    def write_data_to_csv(data, out, date_format=OUTPUT_DATE_FORMAT):
        """
        :param data: [] of {}
            List of dicts
        :param out: str
            Path to output file
        :param date_format: str
            Format output date
        :return: void
            Saves all data to .csv
        """

        for i, transaction in enumerate(data):
            data[i]["date"] = transaction["date"].strftime(date_format)
        write_dicts_to_csv(data, out)


class TransactionType(Enum):
    """ Deposit, withdrawal ... """

    NULL = 0
    DEPOSIT = 1
    WITHDRAWAL = 2
    TRADING = 3
    FUNDING = 4


class Transaction(object):
    """ Exchange transaction """

    def __init__(self, raw_dict, trans_type=TransactionType.TRADING,
                 date_key=None, successful=True):
        """
        :param raw_dict: {}
            Dict containing raw data
        :param trans_type: TransactionType
            Type of transactions
        :param date_key: str
            Key to get date info
        :param successful: bool
            True iff transaction has actually taken place
        """

        object.__init__(self)
        self.raw = raw_dict
        self.transaction_type = trans_type
        if date_key:
            self.date = self.raw[date_key]
        else:
            self.date = None
        self.successful = successful

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

    def is_deposit(self):
        """
        :return: bool
            True iff transaction is a deposit
        """

        return self.transaction_type == TransactionType.DEPOSIT

    def is_withdrawal(self):
        """
        :return: bool
            True iff transaction is a withdrawal
        """

        return self.transaction_type == TransactionType.WITHDRAWAL

    def is_trading(self):
        """
        :return: bool
            True iff transaction is a simple trading
        """

        return self.transaction_type == TransactionType.TRADING

    def has_been_performed(self, successful):
        """
        :param successful: bool
            True iff transaction has actually taken place
        :return: void
            Sets transaction status
        """

        self.successful = successful


class Wallet(object):
    """ A general wallet, tracking addition, deletions and fees """

    def __init__(self, create_date, start_amount=0):
        """
        :param create_date: datetime
            Date of transaction
        ::param start_amount: float
            Amount of currency at start
        """

        object.__init__(self)
        self.balance = float(0)
        self.transactions = []  # list of operations performed

        if start_amount > 0:
            self.add(start_amount, create_date)
        elif start_amount < 0:
            self.remove(start_amount, create_date)

    def add(self, amount, date):
        """
        :param amount: float
            Amount to be added to balance
        :param date: datetime
            Date of transaction
        :return: void
            Adds amount to balance
        """

        self.transactions.append(
            Transaction(
                {
                    "action": "add",
                    "amount": abs(amount),
                    "date": date
                },
                date_key="date"
            )
        )

        self.balance += abs(amount)

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
            Transaction(
                {
                    "action": "remove",
                    "amount": -abs(amount),
                    "date": date
                },
                date_key="date"
            )
        )

        self.balance -= abs(amount)

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
                self.add(transaction["amount"], transaction.date)
            else:
                self.remove(transaction["amount"], transaction.date)

    def get_transactions_dict(self):
        """
        :return: [] of {}
            List of raw transactions
        """

        for transaction in self.transactions:
            yield {
                "date": transaction.date,
                "amount": transaction["amount"],
                "successful": True
            }

    def dates(self):
        """
        :return: [] of datetime
            List of all dates
        """

        return [
            transaction.date for transaction in self.transactions
        ]

    def get_amount(self, date):
        """
        :param date: datetime
            Date of transaction
        :return: float
            Amount exchanged with transaction in specified date
        """

        amount = float(0.0)

        for transaction in self.transactions:
            if transaction.date == date:
                amount += float(transaction["amount"])

        return amount


class Balance(object):
    """ Balance of something, expressed in many coins """

    def __init__(self, wallets):
        """
        :param wallets: {} of Wallet
            List of wallet (and coins)
        """

        object.__init__(self)
        self.wallets = wallets
        nan_keys = [
            key for key in wallets if str(key) == "nan"
        ]
        for key in nan_keys:
            del self.wallets[key]

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
