# !/usr/bin/python3
# coding: utf_8


""" API client to fetch data using Coinmarketcap endpoints """

import os
from datetime import timedelta

from pyhodl.api.models import TorApiClient
from pyhodl.api.price.models import PricesApiClient
from pyhodl.app import get_coin
from pyhodl.config import DATE_TIME_KEY, VALUE_KEY, NAN
from pyhodl.data.coins import Coin
from pyhodl.utils.dates import datetime_to_unix_timestamp_s, datetime_to_str, \
    unix_timestamp_ms_to_datetime, generate_dates
from pyhodl.utils.lists import middle


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
        for coin in coins:  # get all price for each coin
            try:
                raw = self.get_coin_stats(
                    coin, since, until
                )["price_usd"]
                raw = sorted(raw, key=lambda x: x[DATE_TIME_KEY])  # sort
                prices[coin] = raw
            except:
                self.log("Failed getting", coin, "price")
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
        }  # get raw price with 5 minutes interval time
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
        data = []  # price to list of dicts
        for i, date in enumerate(dates):
            if not data or date > data[-1][DATE_TIME_KEY]:  # sorted
                price = {
                    coin: prices[coin][i][VALUE_KEY] for coin in coins
                }
                price[DATE_TIME_KEY] = date
                data.append(price)
        return data
