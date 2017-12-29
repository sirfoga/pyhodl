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

from hal.files.parsers import JSONParser

from pyhodl.models.core import TransactionType


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
    def parse_transaction(self, raw):
        """
        :param raw: {}
            Raw trade
        :return: Transaction
            Parsed Transaction
        """

        return

    @abc.abstractmethod
    def get_transactions_list(self):
        """
        :return: [] of Transaction
            List of transactions of exchange
        """

        raw = self.get_raw_data()

        if self.is_trade(raw):
            coin = raw["commissionAsset"]
        else:
            coin = raw["asset"]


class BinanceParser(CryptoParser):
    """ Parses Binance transactions data """

    def is_trade(self, raw):
        return "isBuyer" in raw

    def is_deposit(self, raw):
        return not self.is_trade(raw) and raw["amount"] >= 0

    def is_withdrawal(self, raw):
        return not self.is_trade(raw) and raw["amount"] < 0

    def get_transactions_list(self):

        amount =

        trade_type = TransactionType.NULL
        if self.is_trade(raw):
            trade_type = TransactionType.TRADING
        elif self.is_deposit(raw):
            trade_type = TransactionType.DEPOSIT
        elif self.is_withdrawal(raw):
            trade_type = TransactionType.WITHDRAWAL


class BitfinexParser(CryptoParser):
    """ Parses Binance transactions data """


class CoinbaseParser(CryptoParser):
    """ Parses Binance transactions data """


class GdaxParser(CryptoParser):
    """ Parses Binance transactions data """
