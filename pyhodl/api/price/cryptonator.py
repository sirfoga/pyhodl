# !/usr/bin/python3
# coding: utf_8


""" API client to fetch data using Cryptonator endpoints """

from datetime import datetime

from pyhodl.api.models import TorApiClient
from pyhodl.api.price.models import PricesApiClient
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
