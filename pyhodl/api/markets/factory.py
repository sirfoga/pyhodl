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


""" Creates API client """
from pyhodl.app import ConfigManager
from pyhodl.config import API_CONFIG

from .binance import BinanceApi
from .bitfinex import BitfinexApi
from .coinbase import CoinbaseApi
from .gdax import GdaxApi


def build_api(raw):
    """
    :param raw: {}
        Api config
    :return: ApiConfig concrete class
        ApiConfig
    """

    if raw["name"] == "binance":
        return BinanceApi(raw)
    elif raw["name"] == "bitfinex":
        return BitfinexApi(raw)
    elif raw["name"] == "coinbase":
        return CoinbaseApi(raw)
    elif raw["name"] == "gdax":
        return GdaxApi(raw)

    raise ValueError("Cannot infer type of API")


class ApiManager(ConfigManager):
    """ Manages your API secrets """

    def __init__(self, config_file=API_CONFIG):
        ConfigManager.__init__(self, config_file)

    def get(self, key):
        out = super().get(key)
        out["name"] = key
        return build_api(out)

    def get_all(self):
        """
        :return: generator of API
            Generate all APIs price
        """

        for key in self.data:
            yield self.get(key)
