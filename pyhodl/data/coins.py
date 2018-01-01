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


class Coin:
    """ Model of a coin traded """

    def __init__(self, symbol, name=None):
        self.symbol = str(symbol).upper()
        self.name = str(name).lower() if name else None

    def get_symbol(self):
        return self.symbol

    def __eq__(self, other):
        if isinstance(other, Coin):
            return other.get_symbol() == other.get_symbol()

        return False


class CryptoCoin(Coin):
    """ Crypto currency model """

    def __init__(self, symbol, name=None, other_names=None):
        Coin.__init__(self, symbol, name)
        self.other_names = [
            str(other).upper() for other in other_names
        ]

    def get_other_names(self):
        return self.other_names


class CoinsNamesTable(JSONParser):
    """ Loads coins database """

    def __init__(self, input_file):
        JSONParser.__init__(self, input_file)

        self.content = self.get_content()

    def get_coins(self):
        return [
            CryptoCoin(
                raw["symbol"],
                name=raw["name"],
                other_names=raw["other_names"]
            ) for raw in self.content
        ]
