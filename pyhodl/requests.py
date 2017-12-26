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

import json
import time
import urllib.parse
import urllib.request

API_URL = "https://min-api.cryptocompare.com/data/pricehistorical"
MAX_COINS_PER_REQUEST = 6
API_ENCODING = {
    "IOTA": "IOT",
    "WAVES": "WAV"
}
API_DECODING = {
    val: key for key, val in API_ENCODING.items()
}


def replace_items(lst, old, new):
    """
    :param lst: []
        List of items
    :param old: obj
        Object to substitute
    :param new: obj
        New object to put in place
    :return: []
        List of items
    """

    for i, val in enumerate(lst):
        if val == old:
            lst[i] = new
    return lst


def encode_coins(coins):
    """
    :param coins: [] of str
        BTC, ETH ...
    :return: [] of str
        Available coins
    """

    for key, val in API_ENCODING.items():
        if key in coins:
            coins = replace_items(coins, key, val)
    return coins


def decode_coins(data):
    """
    :param data: {}
        Result of API calling
    :return: {}
        Original formatted data
    """

    for key, val in API_DECODING.items():
        if key in data:
            data[val] = data[key]
            del data[key]
    return data


def get_api_url(coins, currency, dt):
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
    url = API_URL + "?%s" % params
    return url.replace("%2C", ",")


def get_price(coins, currency, dt):
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

    if len(coins) > MAX_COINS_PER_REQUEST:
        data = get_price(coins[MAX_COINS_PER_REQUEST:], currency, dt)
    else:
        data = {}

    url = get_api_url(
        encode_coins(coins[:MAX_COINS_PER_REQUEST]), currency, dt
    )
    with urllib.request.urlopen(url) as result:
        raw = json.loads(result.read().decode("utf-8"))
        values = raw[currency]
        for coin, price in values.items():
            try:
                price = float(1 / price)
            except:
                price = float("nan")
            data[coin] = price
        data = decode_coins(data)

        for coin in coins:
            if coin not in data:
                data[coin] = float("nan")
        return data
