# !/usr/bin/python3
# coding: utf_8


""" API client core to fetch price data """

import abc
import time

from hal.time.profile import print_time_eta, get_time_eta

from pyhodl.api.models import AbstractApiClient
from pyhodl.config import DATE_TIME_KEY
from pyhodl.utils.dates import generate_dates, datetime_to_str


class PricesApiClient(AbstractApiClient):
    """ Simple price API client """

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

                self.log("got price up to", date)
                print_time_eta(get_time_eta(i + 1, len(dates), start_time))
            except:
                print("Failed getting price for", date)
        return prices

    def get_prices(self, coins, **kwargs):
        """
        :param coins: [] of str
            List of coins
        :param kwargs: **
            Extra args
        :return: [] of {}
            List of coin price
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
