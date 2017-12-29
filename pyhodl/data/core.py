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


""" Parse raw data """

import abc
import os
from datetime import datetime

from hal.files.parsers import JSONParser

from pyhodl.models.core import TransactionType, Transaction


class CryptoParser:
    """ Abstract parser """

    def __init__(self, input_file):
        """
        :param input_file: str
            File to parse
        """

        self.input_file = os.path.join(input_file)  # reformat file path
        self.filename = os.path.basename(self.input_file)

    def get_raw_data(self):
        """
        :return: [] of {}
            List of data from file
        """

        return JSONParser(self.input_file).get_content()

    @abc.abstractmethod
    def is_trade(self, raw):
        """
        :param raw: {}
            Raw trade
        :return: bool
            True iff data is a trading
        """

        return

    @abc.abstractmethod
    def is_deposit(self, raw):
        """
        :param raw: {}
            Raw trade
        :return: bool
            True iff data is a deposit
        """

        return

    @abc.abstractmethod
    def is_withdrawal(self, raw):
        """
        :param raw: {}
            Raw trade
        :return: bool
            True iff data is a withdrawal
        """

        return

    @abc.abstractmethod
    def get_commission(self, raw):
        """
        :param raw: {}
            Raw trade
        :return: Transaction
            Inner commission of transaction (if any). Commission values
            should always be positive floats.
        """

        return

    @abc.abstractmethod
    def get_coins_amounts(self, raw):
        """
        :param raw: {}
            Raw details of transaction
        :return: tuple (str, float, str, float)
            Coin bought, amount bought, coin sold, amount sold
        """

        return

    @abc.abstractmethod
    def get_date(self, raw):
        return

    @abc.abstractmethod
    def is_successful(self, raw):
        """
        :param raw: {}
            Raw details of transaction
        :return: bool
            True iff transaction has completed successfully
        """

        return

    def get_transaction_type(self, raw):
        if self.is_trade(raw):
            return TransactionType.TRADING
        elif self.is_deposit(raw):
            return TransactionType.DEPOSIT
        elif self.is_withdrawal(raw):
            return TransactionType.WITHDRAWAL

        return TransactionType.NULL

    def parse_transaction(self, raw):
        """
        :param raw: {}
            Raw trade
        :return: Transaction
            Parsed Transaction
        """

        coin_bought, amount_bought, coin_sold, amount_sold = \
            self.get_coins_amounts(raw)

        return Transaction(
            raw,
            coin_bought, amount_bought, coin_sold, amount_sold,
            self.get_date(raw),
            self.get_transaction_type(raw),
            self.is_successful(raw),
            self.get_commission(raw)
        )

    def get_transactions_list(self):
        """
        :return: [] of Transaction
            List of transactions of exchange
        """

        raw = self.get_raw_data()
        for transaction in raw:
            try:
                yield self.parse_transaction(transaction)
            except Exception as e:
                print("Cannot parse transaction", transaction, "due to", e)


class BinanceParser(CryptoParser):
    """ Parses Binance transactions data """

    def get_coins_amounts(self, raw):
        if self.is_trade(raw):
            coin_sell, amount_sell = \
                raw["commissionAsset"], float(raw["commission"])
            coin_buy, amount_buy = \
                raw["symbol"].replace(coin_sell, ""), float(raw["qty"])
            return coin_buy, amount_buy, coin_sell, amount_sell
        elif self.is_deposit(raw):
            return raw["asset"], float(raw["amount"]), None, 0
        elif self.is_withdrawal(raw):
            return None, 0, raw["asset"], float(raw["amount"])

        return None, 0, None, 0

    def get_commission(self, raw):
        return None

    def get_date(self, raw):
        if self.is_trade(raw):
            return datetime.fromtimestamp(
                int(raw["time"]) / 1000  # ms -> s
            )
        elif self.is_deposit(raw):
            return datetime.fromtimestamp(
                int(raw["insertTime"]) / 1000  # ms -> s
            )
        elif self.is_withdrawal(raw):
            return datetime.fromtimestamp(
                int(raw["successTime"]) / 1000  # ms -> s
            )

    def is_successful(self, raw):
        if self.is_trade(raw):
            return "commission" in raw
        elif self.is_deposit(raw):
            return int(raw["status"]) == 1
        elif self.is_withdrawal(raw):
            return int(raw["status"]) == 6

        return False

    def is_trade(self, raw):
        return "isBuyer" in raw

    def is_deposit(self, raw):
        return "insertTime" in raw

    def is_withdrawal(self, raw):
        return "applyTime" in raw


class BitfinexParser(CryptoParser):
    """ Parses Binance transactions data """


class CoinbaseParser(CryptoParser):
    """ Parses Binance transactions data """


class GdaxParser(CryptoParser):
    """ Parses Binance transactions data """
