# !/usr/bin/python3
# coding: utf_8


""" Creates API client """
from pyhodl.app import ConfigManager
from pyhodl.config import API_CONFIG

from .binance import BinanceApi
from .bitfinex import BitfinexApi
from .coinbase import CoinbaseApi
from .gdax import GdaxApi


def build_api(raw):
    """
    :param raw: {}
        Api config
    :return: ApiConfig concrete class
        ApiConfig
    """

    if raw["name"] == "binance":
        return BinanceApi(raw)
    elif raw["name"] == "bitfinex":
        return BitfinexApi(raw)
    elif raw["name"] == "coinbase":
        return CoinbaseApi(raw)
    elif raw["name"] == "gdax":
        return GdaxApi(raw)

    raise ValueError("Cannot infer type of API")


class ApiManager(ConfigManager):
    """ Manages your API secrets """

    def __init__(self, config_file=API_CONFIG):
        ConfigManager.__init__(self, config_file)

    def get(self, key):
        out = super().get(key)
        out["name"] = key
        return build_api(out)

    def get_all(self):
        """
        :return: generator of API
            Generate all APIs price
        """

        for key in self.data:
            yield self.get(key)
