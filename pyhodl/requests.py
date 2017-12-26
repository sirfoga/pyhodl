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
    return API_URL + "?%s" % params


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

    url = get_api_url(coins, currency, dt)
    try:
        with urllib.request.urlopen(url) as result:
            raw = json.loads(result.read().decode("utf-8"))
            values = raw[currency]
            data = {}
            for coin, price in values.items():
                if price > 0:  # avoid error in division
                    data[coin] = float(1 / price)
            return data
    except Exception as e:
        print(e)
        return None
