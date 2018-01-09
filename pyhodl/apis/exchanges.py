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

from binance.client import Client as BinanceClient
from ccxt import bitfinex as bitfinex_client
from coinbase.wallet.client import Client as CoinbaseClient
from gdax.authenticated_client import AuthenticatedClient as GdaxClient

from pyhodl.apis.markets.models import ApiConfig


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
        return bitfinex_client({
            "apiKey": self.key,
            "secret": self.secret
        })


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
