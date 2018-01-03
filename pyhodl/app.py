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


""" Config your app """

import os

from hal.files.parsers import JSONParser
from hal.files.save_as import write_dicts_to_json

from pyhodl.config import APP_FOLDER, API_FOLDER, DATA_FOLDER, CRYPTO_COINS
from pyhodl.data.coins import CryptoCoin


class ConfigManager:
    """ Manages config files for app """

    def __init__(self, config_file):
        create_workplace()

        self.config_file = config_file
        self.raw = None
        self.data = {}
        self._check()
        self._read_config()

    def _read_config(self):
        """
        :return: {}
            Config data
        """

        self.raw = JSONParser(self.config_file).get_content()
        for key, value in self.raw.items():
            self.data[key] = value

    def _check(self):
        if not os.path.exists(self.config_file):
            raise ValueError(
                "Empty config file! Please write your settings "
                "and store at " + self.config_file
            )

    def create_config(self):
        """
        :return: void
            Creates config file
        """

        if os.path.exists(self.config_file):
            raise ValueError("Creating new config will erase previous data!")

        write_dicts_to_json({}, self.config_file)  # empty data

    def get(self, key):
        """
        :param key: str
            What you want
        :return: {}
            Item you want
        """

        return self.data[key]

    def save(self):
        """
        :return: void
            Saves app data to local config file
        """

        write_dicts_to_json(self.data, self.config_file)


def create_workplace():
    """
    :return: void
        Creates folder
    """

    for directory in [APP_FOLDER, API_FOLDER, DATA_FOLDER]:
        if not os.path.exists(directory):
            os.makedirs(directory)


def get_coin(symbol):
    """
    :param symbol: str
        Symbol of coin
    :return: CryptoCoin
        Coin if a crypto-coin exists with that name
    """

    candidate = CryptoCoin(symbol, symbol)
    for coin in CRYPTO_COINS:
        if coin.symbol == candidate:
            return coin
