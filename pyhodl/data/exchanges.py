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

from datetime import datetime


class CryptoExchange(object):
    """ Exchange dealing with cryptocoins """

    def __init__(self, transactions):
        """
        :param transactions: [] of Transaction
            List of transactions
        """

        object.__init__(self)
        self.transactions = transactions

    def get_transactions_count(self):
        """
        :return: int
            Number of transactions
        """

        return len(self.transactions)

    def get_balance(self, date=datetime.now()):
        """
        :param date: datetime
            Date and time when you want to get balance
        :return: float

        """
