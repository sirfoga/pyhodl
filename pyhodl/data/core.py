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

from pyhodl.models.exchanges import CryptoExchange
from pyhodl.models.transactions import TransactionType, Transaction


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

        return None, None, None, None

    @abc.abstractmethod
    def get_date(self, raw):
        """
        :param raw: {}
            Raw details of transaction
        :return: datetime
            Date and time of transaction
        """

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
        """
        :param raw: {}
            Raw details of transaction
        :return: TransactionType
            Type of transaction
        """

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
            except:
                print("Cannot parse transaction", transaction)

    def build_exchange(self, exchange_name):
        """
        :param exchange_name: str
            Name of exchange
        :return: CryptoExchange
            List of transactions listed in a exchange
        """

        return CryptoExchange(
            list(self.get_transactions_list()),
            exchange_name
        )
