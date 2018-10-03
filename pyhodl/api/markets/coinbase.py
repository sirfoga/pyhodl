# !/usr/bin/python3
# coding: utf_8


""" Collect data from Coinbase exchange """

from coinbase.wallet.client import Client as CoinbaseClient

from .models import ApiConfig


class CoinbaseApi(ApiConfig):
    """ Api config for Coinbase exchange """

    def get_client(self):
        return CoinbaseClient(
            self.key,
            self.secret
        )
