# !/usr/bin/python3
# coding: utf_8

# Copyright 2017-2018 Stefano Fogarollo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
