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


""" Manage your APIs: add, edit, remove exchanges API """

import abc
import os

from binance.client import Client as BinanceClient
from coinbase.wallet.client import Client as CoinbaseClient
from gdax.authenticated_client import AuthenticatedClient as GdaxClient

from .exchanges import BitfinexClient
from ..app import API_FOLDER, ConfigManager

API_CONFIG = os.path.join(
    API_FOLDER,
    "config.json"
)


class ApiManager(ConfigManager):
    """ Manages your API secrets """

    def __init__(self):
        ConfigManager.__init__(self, API_CONFIG)

    def get(self, key):
        out = super().get(key)
        out["name"] = key
        return ApiConfig.build_api(out)

    def get_all(self):
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

    def to_dict(self):
        return self.raw

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

        try:
            if raw["name"] == "binance":
                return BinanceApi(raw)
            elif raw["name"] == "bitfinex":
                return BitfinexApi(raw)
            elif raw["name"] == "coinbase":
                return CoinbaseApi(raw)
            elif raw["name"] == "gdax":
                return GdaxApi(raw)
            else:
                raise ValueError("Cannot infer type of API")
        except Exception as e:
            print(raw)
            print(e)
            raise ValueError("Cannot infer type of API")


class BinanceApi(ApiConfig):
    """ Api config for Binance exchange """

    def get_client(self):
        return BinanceClient(
            self.key,
            self.secret
        )


class BitfinexApi(ApiConfig):
    """ Api config for Bitfinex exchange """

    def get_client(self):
        return BitfinexClient(
            self.key,
            self.secret
        )


class CoinbaseApi(ApiConfig):
    """ Api config for Coinbase exchange """

    def get_client(self):
        return CoinbaseClient(
            self.key,
            self.secret
        )


class GdaxApi(ApiConfig):
    """ Api config for GDAX exchange """

    def __init__(self, raw):
        ApiConfig.__init__(self, raw)

        self.passphrase = self.raw["passphrase"]

    def get_client(self):
        return GdaxClient(
            self.key,
            self.secret,
            self.passphrase
        )
