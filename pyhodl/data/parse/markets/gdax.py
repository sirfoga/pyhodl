# !/usr/bin/python3
# coding: utf_8


""" Parse raw Gdax data """

import ciso8601

from .coinbase import CoinbaseParser


class GdaxParser(CoinbaseParser):
    """ Parses Binance transactions data """

    def get_coins_amounts(self, raw):
        amount = float(raw["amount"])
        coin = raw["currency"]

        if amount >= 0:  # buy
            return coin, abs(amount), None, 0

        return None, 0, coin, abs(amount)

    def is_trade(self, raw):
        return "product_id" in raw["details"]

    @staticmethod
    def get_transfer_type(raw):
        """
        :param raw: {}
            Raw trade
        :return: str
            Transfer type
        """

        if raw["type"] == "transfer":
            return raw["details"]["transfer_type"]

    def is_withdrawal(self, raw):
        return self.get_transfer_type(raw) == "withdraw"

    def get_commission(self, raw):
        return None  # by default no way to check if transaction has fee or not

    def get_date(self, raw):
        return ciso8601.parse_datetime(raw["created_at"])

    def is_deposit(self, raw):
        return self.get_transfer_type(raw) == "deposit"

    def is_successful(self, raw):
        return True  # always

    def build_exchange(self, exchange_name="gdax"):
        return super().build_exchange(exchange_name)
