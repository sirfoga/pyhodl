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


""" List of crypto-coins supported """

from hal.files.parsers import JSONParser

from pyhodl.utils.lists import do_any_are_in


class Coin:
    """ Model of a coin traded """

    def __init__(self, symbol, name=None):
        self.symbol = str(symbol).upper()
        self.name = str(name).lower() if name else None

    def __eq__(self, other):
        if isinstance(other, Coin):
            return self.symbol == other.symbol

        if isinstance(other, str):  # equals with string
            return self == Coin(other)

        return False

    def __str__(self):
        return self.symbol


class CryptoCoin(Coin):
    """ Crypto currency model """

    def __init__(self, symbol, name=None, other_names=None):
        Coin.__init__(self, symbol, name)
        if other_names:
            self.other_names = [
                str(other).lower() for other in other_names
            ]
        else:
            self.other_names = []

    def __eq__(self, other):
        if super().__eq__(other):
            return True

        if self.name and self.name == other.name:
            return True

        return self.has_same_names(other)

    def has_same_names(self, other):
        """
        :param other: CryptoCoin
            Other coin
        :return: bool
            True iff has same names (or other names)
        """

        if isinstance(other, CryptoCoin) and self.name:
            if self.name in other.other_names:
                return True

            if do_any_are_in(self.other_names, other.other_names):
                return True

        return False


class CoinsNamesTable(JSONParser):
    """ Loads coins database """

    def __init__(self, input_file):
        """
        :param input_file: str
            Use this file as database
        """

        JSONParser.__init__(self, input_file)
        self.content = self.get_content()

    def get_coins(self):
        """
        :return: [] of CryptoCoin
            List of default coins
        """

        return [
            CryptoCoin(
                raw["symbol"],
                name=raw["name"],
                other_names=raw["other_names"]
            ) for raw in self.content
        ]
