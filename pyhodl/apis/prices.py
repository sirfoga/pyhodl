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


""" API requests for historical info """

import os
import time
import urllib.parse
import urllib.request

import requests

from pyhodl.app import DATE_TIME_KEY, NAN, VALUE_KEY
from pyhodl.utils import replace_items, \
    datetime_to_unix_timestamp_ms, unix_timestamp_ms_to_datetime, download, \
    download_with_tor, datetime_to_str


class AbstractApiClient:
    """ Simple bare api client """

    def __init__(self, base_url):
        """
        :param base_url: str
            Base url for API calls
        """

        self.base_url = base_url


class CryptocompareClient(AbstractApiClient):
    """ API interface for official cryptocompare.com APIs """

    BASE_URL = "https://min-api.cryptocompare.com/data/pricehistorical"
    MAX_COINS_PER_REQUEST = 6
    API_ENCODING = {
        "IOTA": "IOT",
        "WAVES": "WAV"
    }
    API_DECODING = {
        val: key for key, val in API_ENCODING.items()
    }

    def __init__(self, base_url=BASE_URL, tor=False):
        AbstractApiClient.__init__(self, base_url)

        self.tor = str(tor) if tor else None  # tor password
        if self.tor:
            print("Handling tor sessions with password:", self.tor)

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

    def get_api_url(self, coins, currency, dt):
        """
        :param coins: [] of str
            BTC, ETH ...
        :param currency: str
            USD, EUR ...
        :param dt: datetime
            Date and time of price
        :return: str
            Url to call
        """

        params = urllib.parse.urlencode(
            {
                "fsym": str(currency),
                "tsyms": ",".join(coins),
                "ts": int(time.mktime(dt.timetuple()))
            }
        )
        url = self.base_url + "?%s" % params
        return url.replace("%2C", ",")

    def get_price(self, coins, currency, dt):
        """
        :param coins: [] of str
            BTC, ETH ...
        :param currency: str
            USD, EUR ...
        :param dt: datetime
            Date and time of price
        :return: {}
            Dict coin -> price
        """

        if len(coins) > self.MAX_COINS_PER_REQUEST:
            data = self.get_price(
                coins[self.MAX_COINS_PER_REQUEST:], currency, dt
            )
        else:
            data = {}

        url = self.get_api_url(
            self._encode_coins(coins[:self.MAX_COINS_PER_REQUEST]),
            currency, dt
        )

        if self.tor:
            result = download_with_tor(url, self.tor, 3)
        else:
            result = download(url)

        result = result.json()  # parse as json
        values = result[currency]
        for coin, price in values.items():
            try:
                price = float(1 / price)
            except:
                price = NAN
            data[coin] = price
        data = self._decode_coins(data)

        for coin in coins:
            if coin not in data:
                data[coin] = NAN
        return data

    def get_prices(self, coins, currency, dates):
        """
        :param coins: [] of str
            BTC, ETH ...
        :param currency: str
            USD, EUR ...
        :param dates: [] of datetime
            Dates to fetch
        :return: generator of {}
            Each dict contains a date and for each coin, its price
        """

        for date in dates:
            try:
                new_prices = self.get_price(coins, currency, date)
                new_prices[DATE_TIME_KEY] = datetime_to_str(date)
                yield new_prices
                print("Got prices up to", date)
            except Exception as e:
                print("Failed getting prices for", date, "due to", e)


class CoinmarketCapClient(AbstractApiClient):
    """ Get coinmarketcap data """

    BASE_URL = "https://graphs.coinmarketcap.com/"

    def __init__(self, base_url=BASE_URL):
        AbstractApiClient.__init__(self, base_url)

    def _create_path(self, action):
        if action == "marketcap":
            return os.path.join("global", "marketcap-total")

    def _create_url(self, action, since, until):
        since = datetime_to_unix_timestamp_ms(since)  # to ms unix
        until = datetime_to_unix_timestamp_ms(until)
        return os.path.join(
            self.base_url,
            self._create_path(action),
            str(since),
            str(until)
        )

    @staticmethod
    def get_raw_data(url):
        r = requests.get(url)
        return r.json()

    def get_market_cap(self, since, until):
        """
        :param since: datetime
            Get data since this date
        :param until: datetime
            Get data until this date
        :return: {} <datetime -> float>
            Each dict key is date and its value is the market cap at the date
        """

        raw_data = self.get_raw_data(
            self._create_url("marketcap", since, until)
        )
        data = raw_data["market_cap_by_available_supply"]
        data = [
            {
                DATE_TIME_KEY: datetime_to_str(
                    unix_timestamp_ms_to_datetime(item[0])
                ),
                VALUE_KEY: float(item[1])
            } for item in data
        ]
        return data

    def get_coin_stats(self, coin, since, until):
        raw_data = self.get_raw_data(
            self._create_url(coin, since, until)
        )
        data = raw_data["market_cap_by_available_supply"]
        data = [
            {
                DATE_TIME_KEY: datetime_to_str(
                    unix_timestamp_ms_to_datetime(item[0])
                ),
                VALUE_KEY: float(item[1])
            } for item in data
        ]
        return data
