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


""" API client core to fetch data """

import abc

from pyhodl.apis.markets.exchanges.binance import BinanceApi
from pyhodl.apis.markets.exchanges.coinbase import CoinbaseApi
from pyhodl.apis.markets.exchanges.gdax import GdaxApi

from pyhodl.apis.markets.bitfinex import BitfinexApi
from pyhodl.app import ConfigManager
from pyhodl.config import API_CONFIG


class ApiManager(ConfigManager):
    """ Manages your API secrets """

    def __init__(self, config_file=API_CONFIG):
        ConfigManager.__init__(self, config_file)

    def get(self, key):
        out = super().get(key)
        out["name"] = key
        return ApiConfig.build_api(out)

    def get_all(self):
        """
        :return: generator of API
            Generate all APIs clients
        """

        for key in self.data:
            yield self.get(key)


class ApiConfig:
    """ Config of API """

    def __init__(self, raw):
        """
        :param raw: {}
            Raw data
        """

        self.raw = raw
        self.key = raw["key"]
        self.secret = raw["secret"]

    @abc.abstractmethod
    def get_client(self):
        """
        :return: ApiClient
            Api client
        """

        return

    @staticmethod
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
