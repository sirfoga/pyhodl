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

import os
from datetime import datetime
from enum import Enum

import pandas as pd

from ..exchanges.core import Transaction


class TransactionType(Enum):
    """ Deposit, withdrawal ... """

    NULL = 0
    DEPOSIT = 1
    WITHDRAWAL = 2
    TRADING = 3
    FUNDING = 4


class Parser(object):
    """ Abstract parser """

    def __init__(self, input_file):
        """
        :param input_file: str
            File to parse
        """

        object.__init__(self)
        self.input_file = os.path.join(input_file)  # reformat file path
        self.filename = os.path.basename(self.input_file)
        self.is_csv = self.input_file.endswith(".csv")
        self.is_excel = self.input_file.endswith(".xlsx")

    def get_raw_data(self):
        """
        :return: pandas.DataFrame
            Raw data from file
        """

        if self.is_excel:
            df = pd.read_excel(self.input_file)
        elif self.is_csv:
            try:
                df = pd.read_csv(self.input_file)
            except ValueError as e:
                if type(e) == pd.errors.ParserError:
                    df = pd.read_csv(self.input_file, skiprows=2)
                else:
                    raise ValueError("File not supported!")
        else:
            raise ValueError("File not supported!")

        return df

    def get_raw_list(self):
        """
        :return: [] of {}
            List of transactions. Each transaction is a dict with keys
            directly from input file
        """

        df = self.get_raw_data()
        return list(df.T.to_dict().values())

    def get_transactions_list(self, date_key, date_format, number_keys):
        """
        :param date_key: str
            Key containing date values
        :param date_format: str
            Date parsing format
        :param number_keys: [] of keys
            List of keys containing numbers to be parsed
        :return: [] of Transaction
            List of transactions of exchange
        """

        raw_list = self.get_raw_list()  # parse raw
        for i, x in enumerate(raw_list):
            raw_list[i][date_key] = datetime.strptime(
                x[date_key],
                date_format
            )  # parse date

            for key in number_keys:
                raw_list[i][key] = float(x[key])
        return [
            Transaction(raw_dict, self.get_type_file(), date_key)
            for raw_dict in raw_list
        ]

    def is_deposit_history(self):
        """
        :return: bool
            True iff file contains history of deposits
        """

        return "depo" in self.filename.lower()

    def is_withdrawal_history(self):
        """
        :return: bool
            True iff file contains history of withdrawals
        """

        return "withd" in self.filename.lower()

    def is_trading_history(self):
        """
        :return: bool
            True iff file contains history of tradings
        """

        return not self.is_deposit_history() and not self.is_withdrawal_history()

    def get_type_file(self):
        """
        :return: TransactionType
            Type of file inferred
        """

        if self.is_deposit_history():
            return TransactionType.DEPOSIT
        elif self.is_withdrawal_history():
            return TransactionType.WITHDRAWAL
        elif self.is_trading_history():
            return TransactionType.TRADING
        else:
            return TransactionType.NULL