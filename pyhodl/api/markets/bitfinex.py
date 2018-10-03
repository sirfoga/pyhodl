# !/usr/bin/python3
# coding: utf_8


""" Collect data from Bitfinex exchange """

from ccxt import bitfinex as bitfinex_client

from .models import ApiConfig


class BitfinexApi(ApiConfig):
    """ Api config for Bitfinex exchange """

    def get_client(self):
        return bitfinex_client({
            "apiKey": self.key,
            "secret": self.secret
        })
