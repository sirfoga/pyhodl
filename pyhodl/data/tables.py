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


""" Parser prices, market cap data and values downloaded with this app """

import os
from bisect import bisect

from hal.files.parsers import JSONParser

from pyhodl.app import HISTORICAL_DATA_FOLDER, DATE_TIME_KEY, INFINITY, \
    VALUE_KEY
from pyhodl.utils import parse_datetime


class DatetimeTable(JSONParser):
    """ Get content from file and load a datetime-based database """

    def __init__(self, input_file, max_error_search):
        """
        :param input_file: str
            File with database to model
        :param max_error_search: float
            When searching for date, returns nearest date found if within
            max error. Should be measured in seconds.
        """

        JSONParser.__init__(self, input_file)

        self.content = {
            parse_datetime(item[DATE_TIME_KEY]): item
            for item in self.get_content()
        }  # date -> raw dict
        self.dates = sorted(self.content.keys())  # sorted list of all dates

        self.max_error = float(max_error_search)  # seconds

    def get_values_on(self, dt):
        """
        :param dt: datetime
            Date to get values of
        :return: {}
            Value on date
        """

        bisect_insert = bisect(self.dates, dt)
        low, high = bisect_insert - 1, bisect_insert  # 2 nearest dates
        low = self.dates[low] if low >= 0 else None
        high = self.dates[high] if high < len(self.dates) else None
        err_low = (dt - low).total_seconds() if low else INFINITY
        err_high = (high - dt).total_seconds() if low else INFINITY

        if err_low <= err_high and err_low <= self.max_error:
            return self.content[low]
        elif err_high <= err_low and err_high <= self.max_error:
            return self.content[high]

        return None

    def get_values_between(self, since, until):
        """
        :param since: datetime
            Get values since this date
        :param until: datetime
            Get values until this date
        :return: generator of {}
            Get all values if key is date in between
        """

        for date in self.dates:
            if since <= date <= until:
                yield self.content[date]


class MarketDataTable(DatetimeTable):
    """ Parse market data files """

    def __init__(self):
        DatetimeTable.__init__(
            self,
            os.path.join(HISTORICAL_DATA_FOLDER, "market_cap.json"),
            3 * 60 * 60  # 3 hours
        )

    def get_value_on(self, dt):
        raw_data = self.get_values_on(dt)
        return raw_data[VALUE_KEY]


class CoinPricesTable(DatetimeTable):
    """ Parse market data files """

    def __init__(self, currency="USD"):
        DatetimeTable.__init__(
            self,
            os.path.join(HISTORICAL_DATA_FOLDER, currency.lower() + ".json"),
            6 * 60 * 60  # 6 hours
        )

        self.base_currency = currency.upper()

    def get_value_on(self, coin, dt):
        """
        :param coin: str
            Coin to convert
        :param dt: datetime
            Date and time of conversion
        :return: float
            Currency value of coin at specified date
        """

        if coin.upper() == self.base_currency:
            return 1.0

        raw_data = self.get_values_on(dt)
        if raw_data:
            return raw_data[coin.upper()]

        return None


COINS_PRICES_TABLE = CoinPricesTable()


def get_coin_prices_table(currency="USD"):
    if currency == "USD":
        return COINS_PRICES_TABLE

    return CoinPricesTable(currency)
