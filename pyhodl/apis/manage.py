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
from hal.files.parsers import JSONParser
from hal.files.save_as import write_dicts_to_json

from .exchanges import BitfinexClient
from ..app import API_FOLDER

API_CONFIG = os.path.join(
    API_FOLDER,
    "config.json"
)


class ApiManager:
    """ Manages your secrets """

    def __init__(self):
        """
        :param config_file: str
            Path to config file
        """

        self.config_file = API_CONFIG
        self.raw = None
        self.data = {}
        self._read_config()

    def _read_config(self):
        """
        :return: {}
            Config data
        """

        self.raw = JSONParser(self.config_file).get_content()
        for key, value in self.raw.items():
            self.data[key] = ApiConfig(value)

    def create_config(self):
        """
        :return: void
            Creates config file
        """

        if os.path.exists(self.config_file):
            raise ValueError("Creating new config will erase previous data!")

        write_dicts_to_json({}, self.config_file)  # empty data

    def get(self, api_name):
        """
        :param api_name: str
            Api name
        :return: {}
            ApiConfig
        """

        return self.data[api_name]

    def save(self):
        out = {}
        for key, value in self.data.items():
            out[key] = value.to_dict()

        write_dicts_to_json(out, self.config_file)


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
    def build_config(raw):
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
