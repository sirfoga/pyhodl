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


""" API client core to fetch prices data """

import abc
import time

from hal.time.profile import print_time_eta, get_time_eta

from pyhodl.apis.models import AbstractApiClient
from pyhodl.config import DATE_TIME_KEY
from pyhodl.data.coins import Coin
from pyhodl.utils.dates import generate_dates, datetime_to_str


class PricesApiClient(AbstractApiClient):
    """ Simple prices API client """

    @abc.abstractmethod
    def get_price(self, coins, date_time, **kwargs):
        """
        :param coins: [] of str
            List of coins
        :param date_time: datetime
            Date and time to get price
        :param kwargs: **
            Extra args
        :return: {}
            Price of coins at specified date and time
        """

        return

    def get_prices_by_date(self, coins, dates, **kwargs):
        """
        :param coins: [] of str
            List of coins
        :param dates: [] of datetime
            Dates and times to get price
        :param kwargs: **
            Extra args
        :return: [] of {}
            Price of coins at specified date and time
        """

        start_time = time.time()
        dates = list(dates)
        prices = []
        for i, date in enumerate(dates):
            try:
                new_prices = self.get_price(coins, date, **kwargs)
                new_prices[DATE_TIME_KEY] = datetime_to_str(date)
                prices.append(new_prices)

                self.log("got prices up to", date)
                print_time_eta(get_time_eta(i + 1, len(dates), start_time))
            except:
                print("Failed getting prices for", date)
        return prices

    def get_prices(self, coins, **kwargs):
        """
        :param coins: [] of str
            List of coins
        :param kwargs: **
            Extra args
        :return: [] of {}
            List of coin prices
        """

        if "dates" not in kwargs:  # args since, until and hours provided
            kwargs["dates"] = generate_dates(
                kwargs["since"],
                kwargs["until"],
                kwargs["hours"]
            )

        dates = kwargs["dates"]

        for key in ["since", "until", "hours", "dates"]:
            if key in kwargs:
                del kwargs[key]

        return self.get_prices_by_date(coins, dates, **kwargs)


def get_market_cap(since, until):
    """
    :param since: datetime
        Get data since this date
    :param until: datetime
        Get data until this date
    :return: [] of {}
        Crypto market cap at specified dates
    """

    client = CoinmarketCapClient()
    return client.get_market_cap(since, until)


def get_client(currency, tor):
    """
    :param currency: str
        Currency to get price
    :param tor: *
        Tor arg
    :return: ApiClient
        Client to get price with
    """

    if Coin(currency) in CryptocompareClient.AVAILABLE_FIAT:
        return CryptocompareClient(tor=tor)  # better client (use as default)

    return CoinmarketCapClient(tor=tor)


def get_price_on_dates(coins, currency, dates, tor):
    """
    :param coins: [] of str
        List of coins
    :param currency: str
        Convert prices to this currency
    :param dates: [] of datetime
        Get prices on these dates
    :param tor: str or None
        Password to access tor proxy
    :return: [] of {}
        List of prices of coins at dates
    """

    client = get_client(currency, tor)
    return client.get_prices(
        coins, dates=dates, hours=6, currency=currency
    )


def get_price_on_date(coins, currency, date_time, tor):
    """
    :param coins: [] of str
        List of coins
    :param currency: str
        Convert prices to this currency
    :param date_time: datetime
        Get prices on date
    :param tor: str or None
        Password to access tor proxy
    :return: [] of {}
        List of prices of coins at dates
    """

    client = get_client(currency, tor)
    return client.get_price(
        coins, date_time=date_time, currency=currency
    )
