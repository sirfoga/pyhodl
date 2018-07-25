# !/usr/bin/python3
# coding: utf_8


""" Collect data from Binance exchange """

from binance.client import Client as BinanceClient

from .models import ApiConfig


class BinanceApi(ApiConfig):
    """ Api config for Binance exchange """

    def get_client(self):
        return BinanceClient(
            self.key,
            self.secret
        )
