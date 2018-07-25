# !/usr/bin/python3
# coding: utf_8


""" Parse raw Bitfinex data """

from datetime import datetime

from pyhodl.core.transactions import Commission, CoinAmount
from ..core import CryptoParser


class BitfinexParser(CryptoParser):
    """ Parses Binance transactions data """

    @staticmethod
    def fix_coin_name(coin):
        """
        :param coin: str
            Raw coin name
        :return: str
            Coin name (fixed)
        """

        if coin.lower() == "dsh":
            return "DASH"

        return coin.upper()

    @staticmethod
    def get_coins_amount_traded(raw):
        coin_buy, coin_sell = raw["symbol"][:3], raw["symbol"][3:]
        coin_buy, coin_sell = \
            BitfinexParser.fix_coin_name(coin_buy), \
            BitfinexParser.fix_coin_name(coin_sell)
        buy_amount = float(raw["amount"])
        sell_amount = buy_amount * float(raw["price"])
        if raw["type"] == "Buy":
            return coin_buy, buy_amount, coin_sell, sell_amount

        return coin_sell, sell_amount, coin_buy, buy_amount

    def get_coin_moved(self, raw, coin_key="currency", amount_key="amount"):
        return super().get_coin_moved(raw, coin_key, amount_key)

    def is_trade(self, raw):
        return raw["type"] in ["Sell", "Buy"]

    def is_withdrawal(self, raw):
        return raw["type"] == "WITHDRAWAL"

    def get_fee(self, raw):
        """
        :param raw: {}
            Raw trade
        :return: tuple (str, float)
            Coin fee and amount
        """

        if self.is_trade(raw):
            return raw["fee_currency"], abs(float(raw["fee_amount"]))
        elif self.is_deposit(raw):
            return raw["currency"], abs(float(raw["fee"]))

        return None, None

    def get_commission(self, raw):
        fee_coin, amount = self.get_fee(raw)
        return Commission(
            raw, CoinAmount(fee_coin, amount, False), self.get_date(raw),
            self.is_successful(raw)
        )

    def get_date(self, raw):
        return datetime.fromtimestamp(int(float(raw["timestamp"])))

    def is_deposit(self, raw):
        return raw["type"] == "DEPOSIT"

    def is_successful(self, raw):
        if self.is_trade(raw):
            return float(raw["fee_amount"]) <= 0
        elif self.is_deposit(raw) or self.is_withdrawal(raw):
            return raw["status"] == "COMPLETED"

        return False

    def build_exchange(self, exchange_name="bitfinex"):
        return super().build_exchange(exchange_name)
