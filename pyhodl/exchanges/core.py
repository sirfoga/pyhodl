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

from hal.files.save_as import write_dicts_to_csv

from pyhodl.apis.prices import get_price
from pyhodl.utils import generate_dates


class CryptoExchange:
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

    def __init__(self, transactions, exchange_name):
        """
        :param transactions: [] of Transaction
            List of transactions
        """

        self.transactions = transactions
        if not self.transactions:
            raise ValueError("Creating exchange with no past transaction!")
        self.exchange_name = str(exchange_name)

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
