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


""" API clients to fetch prices data """

import os
import urllib.parse
from datetime import timedelta, datetime

from pyhodl.apis.models import TorApiClient
from pyhodl.apis.prices.models import PricesApiClient
from pyhodl.app import get_coin
from pyhodl.config import FIAT_COINS, NAN, DATE_TIME_KEY, VALUE_KEY
from pyhodl.data.coins import Coin
from pyhodl.utils.dates import generate_dates, datetime_to_unix_timestamp_s, \
    unix_timestamp_ms_to_datetime, datetime_to_str, get_delta_seconds
from pyhodl.utils.misc import replace_items, middle


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
            print(url)
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
        real_time_interval = 60 * 5  # 5 minutes
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
            coin: float(1 / price) if price > 0 else 0  # convert from USD
            for coin, price in prices.items()
        }


class CoinmarketCapClient(PricesApiClient, TorApiClient):
    """ Get coinmarketcap.com APIs data """

    BASE_URL = "https://graphs.coinmarketcap.com/"
    AVAILABLE_FIAT = [Coin("USD")]
    TIME_FRAME = timedelta(minutes=5)  # API does not provide exact timing

    def __init__(self, base_url=BASE_URL, tor=False):
        PricesApiClient.__init__(self, base_url)
        TorApiClient.__init__(self, tor)

    @staticmethod
    def _create_path(action):
        if action == "marketcap":
            return os.path.join("global", "marketcap-total")

        # action is a coin
        return os.path.join(
            "currencies", get_coin(action).name
        )

    def _create_url(self, action, since, until):
        """
        :param action: str
            Action to take
        :param since: datetime
            Get data since this time
        :param until: datetim
            Get data until this time
        :return: str
            Url to get data
        """

        since = datetime_to_unix_timestamp_s(since)  # to ms unix
        until = datetime_to_unix_timestamp_s(until)
        return os.path.join(
            self.base_url,
            self._create_path(action),
            str(since),
            str(until)
        )

    def download(self, url):
        return super().download(url).json()  # parse as json

    def get_market_cap(self, since, until):
        """
        :param since: datetime
            Get data since this date
        :param until: datetime
            Get data until this date
        :return: {} <datetime -> float>
            Each dict key is date and its value is the market cap at the date
        """

        raw_data = self.download(self._create_url("marketcap", since, until))
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
        """
        :param coin: str
            Coin to fetch
        :param since: datetime
            Get data since this date
        :param until: datetime
            Get data until this date
        :return: {}
            Coin stats
        """

        raw_data = self.download(self._create_url(coin, since, until))
        data = {}
        for category, values in raw_data.items():
            data[category] = [
                {
                    DATE_TIME_KEY: unix_timestamp_ms_to_datetime(item[0]),
                    VALUE_KEY: float(item[1])
                } for item in values
            ]
        return data

    def get_price(self, coins, date_time, **kwargs):
        data = {}
        for coin in coins:
            try:
                stats = self.get_coin_stats(
                    coin,
                    date_time - self.TIME_FRAME,
                    date_time + self.TIME_FRAME
                )
                price = middle(stats["price_usd"])[VALUE_KEY]
                data[coin] = price
            except:
                data[coin] = NAN
        return data

    def get_raw_prices(self, coins, **kwargs):
        """
        :param coins: [] of str
            Coins to fetch
        :param kwargs: **
            Additional args
        :return: {}
            Each key is a coin; each value is a list of dict with date and
            coin price.
        """

        since = kwargs["since"]
        until = kwargs["until"]
        prices = {}  # dict <str coin -> [ dict <date -> price> ]>
        for coin in coins:  # get all prices for each coin
            try:
                raw = self.get_coin_stats(
                    coin, since, until
                )["price_usd"]
                raw = sorted(raw, key=lambda x: x[DATE_TIME_KEY])  # sort
                prices[coin] = raw
            except:
                self.log("Failed getting", coin, "prices")
        return prices

    def get_prices(self, coins, **kwargs):
        if "dates" in kwargs:
            dates = kwargs["dates"]
        else:  # args since, until and hours provided
            dates = generate_dates(
                kwargs["since"] - self.TIME_FRAME,
                kwargs["until"] + self.TIME_FRAME,
                24  # day intervals
            )

        prices = {
            coin: [] for coin in coins
        }  # get raw prices with 5 minutes interval time
        for i, date in enumerate(dates[1:]):
            new_prices = self.get_raw_prices(
                coins, since=dates[i - 1], until=date
            )
            for coin in new_prices:  # same keys
                prices[coin] += new_prices[coin]
                print("Found new datetime interval",
                      new_prices[coin][0][DATE_TIME_KEY], "->",
                      new_prices[coin][-1][DATE_TIME_KEY])

        dates = [
            data[DATE_TIME_KEY]
            for data in prices[coins[0]]  # take dates from first coin
        ]
        data = []  # prices to list of dicts
        for i, date in enumerate(dates):
            if not data or date > data[-1][DATE_TIME_KEY]:  # sorted
                price = {
                    coin: prices[coin][i][VALUE_KEY] for coin in coins
                }
                price[DATE_TIME_KEY] = date
                data.append(price)
        return data


class CryptonatorClient(PricesApiClient, TorApiClient):
    """ Get cryptonator.com APIs data """

    BASE_URL = "https://api.cryptonator.com/api/ticker/"
    API_ENCODING = {
        "IOTA": "IOT",
        "WAV": "WAVES"
    }
    API_DECODING = {
        val: key for key, val in API_ENCODING.items()
    }

    def __init__(self, base_url=BASE_URL, tor=False):
        PricesApiClient.__init__(self, base_url)
        TorApiClient.__init__(self, tor)

    def download(self, url):
        return super().download(url).json()  # parse as json

    def _create_url(self, coin, currency):
        """
        :param coin: str
            Coin to convert to currency
        :param currency: str
            Currency
        :return: str
            Url to get data
        """

        return self.base_url + coin.lower() + "-" + currency.lower()

    def get_price(self, coins, date_time, **kwargs):
        now = datetime.now()
        real_time_interval = 60 * 10  # 10 minutes
        if abs(get_delta_seconds(now, date_time)) > real_time_interval:
            raise ValueError(self.class_name, "does only real-time "
                                              "conversions!")

        raise ValueError("Not fully implemented!")
