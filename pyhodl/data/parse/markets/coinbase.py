# !/usr/bin/python3
# coding: utf_8


""" Parse raw Coinbase data """

import ciso8601

from pyhodl.core.transactions import Commission, CoinAmount
from ..core import CryptoParser


class CoinbaseParser(CryptoParser):
    """ Parses Coinbase transactions data """

    def get_coin_moved(self, raw, coin_key="currency", amount_key="amount"):
        return super().get_coin_moved(raw["amount"], coin_key, amount_key)

    @staticmethod
    def get_coins_amount_traded(raw):
        coin, currency = \
            raw["amount"]["currency"], raw["native_amount"]["currency"]

        if coin != currency:  # otherwise just a fiat log to discard
            coin_buy, amount_buy = \
                currency, abs(float(raw["native_amount"]["amount"]))
            coin_sell, amount_sell = \
                coin, abs(float(raw["amount"]["amount"]))

            if raw["type"] == "sell":
                return coin_buy, amount_buy, coin_sell, amount_sell

            return coin_sell, amount_sell, coin_buy, amount_buy

        return None, 0, None, 0

    def is_trade(self, raw):
        return raw["type"] in ["buy", "sell"]

    def is_withdrawal(self, raw):
        amount = float(raw["amount"]["amount"])
        native_amount = float(raw["native_amount"]["amount"])
        return amount < 0 and native_amount < 0

    def get_commission(self, raw):
        try:
            commission_data = raw["network"]
            return Commission(
                commission_data,
                CoinAmount(
                    commission_data["transaction_fee"]["currency"],
                    commission_data["transaction_fee"]["amount"],
                    False
                ),
                self.get_date(raw),
                commission_data["status"] == "confirmed"
            )
        except:
            return None

    def get_date(self, raw):
        return ciso8601.parse_datetime(raw["updated_at"])

    def is_deposit(self, raw):
        amount = float(raw["amount"]["amount"])
        native_amount = float(raw["native_amount"]["amount"])
        return amount >= 0 and native_amount >= 0

    def is_successful(self, raw):
        return raw["status"] == "completed"

    def get_transactions_list(self):
        raw = self.get_raw_data()
        for _, transactions in raw.items():
            for transaction in transactions:
                yield self.parse_transaction(transaction)

    def build_exchange(self, exchange_name="coinbase"):
        return super().build_exchange(exchange_name)
