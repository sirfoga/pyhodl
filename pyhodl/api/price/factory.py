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


""" Creates API client """

from pyhodl.data.coins import Coin
from .coinmarketcap import CoinmarketCapClient
from .cryptocompare import CryptocompareClient


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
        Convert price to this currency
    :param dates: [] of datetime
        Get price on these dates
    :param tor: str or None
        Password to access tor proxy
    :return: [] of {}
        List of price of coins at dates
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
        Convert price to this currency
    :param date_time: datetime
        Get price on date
    :param tor: str or None
        Password to access tor proxy
    :return: [] of {}
        List of price of coins at dates
    """

    client = get_client(currency, tor)
    return client.get_price(
        coins, date_time=date_time, currency=currency
    )
