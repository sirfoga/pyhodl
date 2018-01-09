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


""" API client to fetch data using Cryptonator endpoints """

from datetime import datetime

from pyhodl.apis.models import TorApiClient
from pyhodl.apis.prices.models import PricesApiClient
from pyhodl.config import SECONDS_IN_MIN
from pyhodl.utils.dates import get_delta_seconds


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
        real_time_interval = SECONDS_IN_MIN * 10  # 10 minutes
        if abs(get_delta_seconds(now, date_time)) > real_time_interval:
            raise ValueError(self.class_name, "does only real-time "
                                              "conversions!")

        raise ValueError("Not fully implemented!")
