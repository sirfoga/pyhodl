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


""" API client to fetch data using Cryptocompare endpoints """

import urllib.parse
from datetime import datetime

from pyhodl.apis.models import TorApiClient
from pyhodl.apis.prices.models import PricesApiClient
from pyhodl.config import NAN, SECONDS_IN_MIN
from pyhodl.data.coins import FIAT_COINS
from pyhodl.utils.dates import get_delta_seconds, datetime_to_unix_timestamp_s
from pyhodl.utils.lists import replace_items
from pyhodl.utils.misc import get_ratio


class CryptocompareClient(PricesApiClient, TorApiClient):
    """ API interface for official cryptocompare.com APIs """

    BASE_URL = "https://min-api.cryptocompare.com/data/"
    MAX_COINS_PER_REQUEST = 6
    API_ENCODING = {
        "IOTA": "IOT",
        "WAV": "WAVES"
    }
    API_DECODING = {
        val: key for key, val in API_ENCODING.items()
    }
    AVAILABLE_FIAT = FIAT_COINS

    def __init__(self, base_url=BASE_URL, tor=False):
        PricesApiClient.__init__(self, base_url)
        TorApiClient.__init__(self, tor)

    def _encode_coins(self, coins):
        """
        :param coins: [] of str
            BTC, ETH ...
        :return: [] of str
            Available coins
        """

        for key, val in self.API_ENCODING.items():
            if key in coins:
                coins = replace_items(coins, key, val)
        return coins

    def _decode_coins(self, data):
        """
        :param data: {}
            Result of API calling
        :return: {}
            Original formatted data
        """

        for key, val in self.API_DECODING.items():
            if key in data:
                data[val] = data[key]
                del data[key]
        return data

    def download(self, url):
        return super().download(url).json()  # parse as json

    @staticmethod
    def _parse_result(result):
        """
        :param result: {}
            Raw result of API
        :return: {}
            Dict with prices for each coin
        """

        values = list(result.values())[0]
        if isinstance(values, dict):
            return values

        return result

    def fetch_raw_prices(self, coins, date_time, currency):
        """
        :param coins: [] of str
            List of coins
        :param date_time: datetime
            Date and time to get price
        :param currency: str
            Currency to convert to
        :return: {}
            List of raw prices
        """

        if len(coins) <= self.MAX_COINS_PER_REQUEST:
            url = self._create_url(
                self._encode_coins(coins), date_time, currency=currency
            )
            result = self.download(url)
            return self._parse_result(result)  # parse data

        long_data = self.fetch_raw_prices(
            coins[self.MAX_COINS_PER_REQUEST:], date_time,
            currency=currency
        )  # get other data
        data = self.fetch_raw_prices(
            coins[:self.MAX_COINS_PER_REQUEST], date_time, currency=currency
        )
        return {**data, **long_data}  # merge dicts

    def fetch_prices(self, coins, date_time, currency):
        """
        :param coins: [] of str
            List of coins
        :param date_time: datetime
            Date and time to get price
        :param currency: str
            Currency to convert to
        :return: {}
            List of prices of each coin
        """

        data = self.fetch_raw_prices(coins, date_time, currency)
        data = self._decode_coins(data)

        for coin in coins:
            if coin not in data:
                data[coin] = NAN

        for coin, price in data.items():
            if price == 0.0:
                data[coin] = NAN

        return data

    def _create_url(self, coins, date_time, **kwargs):
        """
        :param coins: [] of str
            BTC, ETH ...
        :param date_time: datetime
            Date and time of price
        :return: str
            Url to call
        """

        now = datetime.now()
        real_time_interval = SECONDS_IN_MIN * 5  # 5 minutes
        real_time = abs(get_delta_seconds(now, date_time)) < real_time_interval

        if real_time:
            url = self.base_url + "price"
            params = {
                "fsym": str(kwargs["currency"]),
                "tsyms": ",".join(coins)
            }
        else:
            url = self.base_url + "pricehistorical"  # past data
            params = {
                "fsym": str(kwargs["currency"]),
                "tsyms": ",".join(coins),
                "ts": datetime_to_unix_timestamp_s(date_time)
            }

        params = urllib.parse.urlencode(params)
        url += "?%s" % params
        return url.replace("%2C", ",")

    def get_price(self, coins, date_time, **kwargs):
        currency = kwargs["currency"]
        prices = self.fetch_raw_prices(coins, date_time, currency)
        return {
            coin: get_ratio(1, price) for coin, price in prices.items()
        }
