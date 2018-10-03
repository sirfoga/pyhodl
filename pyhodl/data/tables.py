# !/usr/bin/python3
# coding: utf_8


""" Parser price, market cap data and values downloaded with this app """

import os
from bisect import bisect

from hal.files.parsers import JSONParser

from pyhodl.config import HISTORICAL_DATA_FOLDER, DATE_TIME_KEY, VALUE_KEY, \
    INFINITY, get_coin_historical_data_file, SECONDS_IN_HOUR
from pyhodl.utils.dates import parse_datetime


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

    def get_content(self):
        if os.path.exists(self.path):
            return super().get_content()

        return {}

    def get_values_on(self, date_time):
        """
        :param date_time: datetime
            Date to get values of
        :return: {}
            Value on date
        """

        bisect_insert = bisect(self.dates, date_time)

        low, high = bisect_insert - 1, bisect_insert  # 2 nearest dates
        low = self.dates[low] if low >= 0 else None
        high = self.dates[high - 1] if high <= len(self.dates) else None

        err_low = (date_time - low).total_seconds() if low else INFINITY
        err_high = (high - date_time).total_seconds() if low else INFINITY
        errors = [err_low, err_high, self.max_error]

        if min(errors) == err_low:
            return self.content[low]
        elif min(errors) == err_high:
            return self.content[high]

    def get_values_on_dates(self, dates):
        """
        :param dates: [] of datetime
            List of dates to fetch
        :return: [] of float
            List of values in dates
        """

        for date in dates:
            yield self.get_values_on(date)

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
            3 * SECONDS_IN_HOUR  # 3 hours
        )

    def get_value_on(self, date_time):
        """
        :param date_time: datetime
            Date and time to fetch
        :return: *
            Data at specified date and time
        """

        raw_data = self.get_values_on(date_time)
        return raw_data[VALUE_KEY]


class CoinPricesTable(DatetimeTable):
    """ Parse market data files """

    def __init__(self, currency):
        DatetimeTable.__init__(
            self,
            get_coin_historical_data_file(currency),
            24 * SECONDS_IN_HOUR  # a day
        )

        self.base_currency = currency.upper()

    def get_value_on(self, coin, date_time):
        """
        :param coin: str
            Coin to convert
        :param date_time: datetime
            Date and time of conversion
        :return: float
            Currency value of coin at specified date
        """

        if coin.upper() == self.base_currency:
            return 1.0

        raw_data = self.get_values_on(date_time)
        if raw_data:
            return raw_data[coin.upper()]

        return None


COINS_PRICES_TABLE = CoinPricesTable("USD")


def get_coin_prices_table(currency="USD"):
    """
    :param currency: str
        Convert price to this currency
    :return: CoinPricesTable
        Database of price
    """

    if currency == "USD":
        return COINS_PRICES_TABLE

    return CoinPricesTable(currency)
