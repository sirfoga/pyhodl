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


""" Updates exchanges data """

import abc

from binance.client import Client as BinanceClient
from coinbase.wallet.client import Client as CoinbaseClient
from gdax.authenticated_client import AuthenticatedClient as GdaxClient

from ..apis.exchanges import BitfinexClient


class ExchangeUpdater:
    """ Abstract exchange updater """

    def __init__(self, api_client, data_folder):
        self.client = api_client
        self.folder = data_folder

    @abc.abstractmethod
    def get_transactions(self):
        return

    @staticmethod
    def build_updater(api_client, data_folder):
        if type(api_client) == type(BinanceClient):
            return BinanceUpdater(api_client, data_folder)
        elif type(api_client) == type(BitfinexClient):
            return BitfinexUpdater(api_client, data_folder)
        elif type(api_client) == type(CoinbaseClient):
            return CoinbaseUpdater(api_client, data_folder)
        elif type(api_client) == type(GdaxClient):
            return GdaxUpdater(api_client, data_folder)


class BinanceUpdater(ExchangeUpdater):
    """ Updates Binance data """

    def get_transactions(self):
        return []


class BitfinexUpdater(ExchangeUpdater):
    """ Updates Bitfinex data """

    def get_transactions(self):
        return []


class CoinbaseUpdater(ExchangeUpdater):
    """ Updates Coinbase data """

    def get_transactions(self):
        return []


class GdaxUpdater(ExchangeUpdater):
    """ Updates Gdax data """

    def get_transactions(self):
        return []
