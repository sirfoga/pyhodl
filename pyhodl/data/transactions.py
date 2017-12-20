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


""" Deal with transactions data """


class Transaction(object):
    """ Exchange transaction """

    def __init__(self, raw_dict, date_key):
        """
        :param raw_dict: {}
            Dict containing raw data
        :param date_key: str
            Key to get date info
        """

        object.__init__(self)
        self.raw = raw_dict
        self.date = self.raw[date_key]

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
                if str(item) in str(value):
                    return True
            except:
                pass
        return False

    def __getitem__(self, key):
        return self.raw[key]


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
