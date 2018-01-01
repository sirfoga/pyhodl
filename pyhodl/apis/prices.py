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

import abc
import os
import urllib.parse
import urllib.request
from datetime import timedelta

from pyhodl.app import DATE_TIME_KEY, NAN, VALUE_KEY, FIAT_COINS, \
    get_coin_by_symbol
from pyhodl.data.coins import Coin
from pyhodl.logs import Logger
from pyhodl.utils import replace_items, \
    datetime_to_unix_timestamp_ms, unix_timestamp_ms_to_datetime, download, \
    download_with_tor, datetime_to_str, datetime_to_unix_timestamp_s, middle, \
    generate_dates


class AbstractApiClient(Logger):
    """ Simple bare api client """

    def __init__(self, base_url):
        """
        :param base_url: str
            Base url for API calls
        """

        Logger.__init__(self)
        self.base_url = base_url


class PricesApiClient(AbstractApiClient):
    """ Simple prices API client """

    @abc.abstractmethod
    def get_price(self, coins, dt, **kwargs):
        return

    def get_prices_by_date(self, coins, dates, **kwargs):
        for date in dates:
            try:
                new_prices = self.get_price(coins, date, kwargs)
                new_prices[DATE_TIME_KEY] = datetime_to_str(date)
                yield new_prices
                print("Got prices up to", date)
            except Exception as e:
                print("Failed getting prices for", date, "due to", e)

    def get_prices(self, coins, **kwargs):
        if "dates" in kwargs:
            dates = kwargs["dates"]
        else:  # args since, until and hours provided
            dates = generate_dates(
                kwargs["since"],
                kwargs["until"],
                kwargs["hours"]
            )

        return list(
            self.get_prices_by_date(coins, dates, **kwargs)
        )


class TorApiClient:
    """ Access API methods via tor """

    def __init__(self, tor=False):
        self.tor = str(tor) if tor else None  # tor password
        if self.tor:
            print("Handling tor sessions with password:", self.tor)

    def download(self, url):
        if self.tor:
            return download_with_tor(url, self.tor, 3)

        return download(url)


class CryptocompareClient(PricesApiClient, TorApiClient):
    """ API interface for official cryptocompare.com APIs """

    BASE_URL = "https://min-api.cryptocompare.com/data/pricehistorical"
    MAX_COINS_PER_REQUEST = 6
    API_ENCODING = {
        "IOTA": "IOT"
    }
    API_DECODING = {
        val: key for key, val in API_ENCODING.items()
    }
    AVAILABLE_FIAT = FIAT_COINS

    def __init__(self, base_url=BASE_URL, tor=False):
        AbstractApiClient.__init__(self, base_url)
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

    def get_api_url(self, coins, dt, **kwargs):
        """
        :param coins: [] of str
            BTC, ETH ...
        :param dt: datetime
            Date and time of price
        :return: str
            Url to call
        """

        params = urllib.parse.urlencode(
            {
                "fsym": str(kwargs["currency"]),
                "tsyms": ",".join(coins),
                "ts": datetime_to_unix_timestamp_s(dt)
            }
        )
        url = self.base_url + "?%s" % params
        return url.replace("%2C", ",")

    def get_price(self, coins, dt, **kwargs):
        currency = kwargs["currency"]
        if len(coins) > self.MAX_COINS_PER_REQUEST:
            data = self.get_price(
                coins[self.MAX_COINS_PER_REQUEST:], dt, currency=currency
            )
        else:
            data = {}

        url = self.get_api_url(
            self._encode_coins(coins[:self.MAX_COINS_PER_REQUEST]),
            dt, currency=currency
        )
        result = self.download(url)
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


class CoinmarketCapClient(PricesApiClient, TorApiClient):
    """ Get coinmarketcap.com APIs data """

    BASE_URL = "https://graphs.coinmarketcap.com/"
    AVAILABLE_FIAT = [Coin("USD")]
    TIME_FRAME = timedelta(minutes=5)  # API does not provide exact timing

    def __init__(self, base_url=BASE_URL, tor=False):
        AbstractApiClient.__init__(self, base_url)
        TorApiClient.__init__(self, tor)

    def _create_path(self, action):
        if action == "marketcap":
            return os.path.join("global", "marketcap-total")

        # action is a coin
        return os.path.join(
            "currencies", get_coin_by_symbol(action).name
        )

    def _create_url(self, action, since, until):
        since = datetime_to_unix_timestamp_ms(since)  # to ms unix
        until = datetime_to_unix_timestamp_ms(until)
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

    def get_price(self, coins, dt, **kwargs):
        data = {}
        for coin in coins:
            try:
                stats = self.get_coin_stats(
                    coin,
                    dt - self.TIME_FRAME,
                    dt + self.TIME_FRAME
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
            except Exception as e:
                self.log("Failed getting", coin, "prices due to", e)
        return prices

    def get_prices(self, coins, **kwargs):
        since = kwargs["since"] - self.TIME_FRAME
        until = kwargs["until"] + self.TIME_FRAME
        dates = list(generate_dates(since, until, hours=23))  # day intervals
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


def get_market_cap(since, until):
    client = CoinmarketCapClient()
    return client.get_market_cap(since, until)


def get_prices(coins, currency, since, until, tor):
    if Coin(currency) in CoinmarketCapClient.AVAILABLE_FIAT:
        client = CoinmarketCapClient(tor=tor)  # better client (use as default)
    else:
        client = CryptocompareClient(tor=tor)

    return client.get_prices(
        coins, since=since, until=until, hours=6, currency=currency
    )
