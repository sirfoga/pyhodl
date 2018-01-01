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

from enum import Enum

from hal.files.parsers import JSONParser


class FiatCoins(Enum):
    USD = "USD"
    EUR = "EUR"


class CryptoCoin:
    """ Crypto currency model """

    def __init__(self, codename, name=None, other_names=None):
        self.codename = str(codename).upper()
        self.name = str(name).lower()
        self.other_names = [
            str(other).upper() for other in other_names
        ]

    def get_name(self):
        return self.name

    def get_other_names(self):
        return self.other_names

    def get_code(self):
        return self.codename

    def __eq__(self, other):
        if isinstance(other, CryptoCoin):
            return other.get_name() == other.get_name()

        return False


class CoinsNamesTable(JSONParser):
    """ Loads coins database """

    def __init__(self, input_file):
        JSONParser.__init__(self, input_file)

        self.content = self.get_content()

    def get_coins(self):
        return [
            CryptoCoin(
                raw["codename"],
                name=raw["name"],
                other_names=raw["other_names"]
            ) for raw in self.content
        ]
