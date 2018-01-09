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


""" Parse raw Binance data """

from datetime import datetime

from pyhodl.core.transactions import Commission, CoinAmount
from pyhodl.data.parse.core import CryptoParser


class BinanceParser(CryptoParser):
    """ Parses Binance transactions data """

    def get_coin_moved(self, raw, coin_key="asset", amount_key="amount"):
        return super().get_coin_moved(raw, coin_key, amount_key)

    @staticmethod
    def get_coins_amount_traded(raw):
        coin_buy, coin_sell = BinanceParser.get_coins_traded(raw)
        amount_buy, amount_sell = BinanceParser.get_amount_traded(raw)
        return coin_buy, amount_buy, coin_sell, amount_sell

    @staticmethod
    def get_coins_traded(raw):
        """
        :param raw: {}
            Raw details of transaction
        :return: tuple (str, str)
            Coin bought, coin sold, in case of trading data
        """

        market = raw["symbol"]
        if market.endswith("USDT"):
            coin_buy, coin_sell = market.replace("USDT", ""), "USDT"
        else:
            coin_buy, coin_sell = market[:-3], market[-3:]

        if raw["isBuyer"]:
            return coin_buy, coin_sell

        return coin_sell, coin_buy

    @staticmethod
    def get_amount_traded(raw):
        """
        :param raw: {}
            Raw details of transaction
        :return: tuple (float, float)
            Amount bought, amount sold in case of trading data
        """

        amount_buy = float(raw["qty"])
        amount_sell = float(raw["price"]) * amount_buy

        if raw["isBuyer"]:
            return amount_buy, amount_sell

        return amount_sell, amount_buy

    def get_commission(self, raw):
        if "commissionAsset" in raw:
            return Commission(
                raw,
                CoinAmount(
                    raw["commissionAsset"],
                    raw["commission"],
                    False
                ),
                self.get_date(raw),
                self.is_successful(raw)
            )
        return None

    def get_date(self, raw):
        if self.is_trade(raw):
            return datetime.fromtimestamp(
                int(raw["time"]) / 1000  # ms -> s
            )
        elif self.is_deposit(raw):
            return datetime.fromtimestamp(
                int(raw["insertTime"]) / 1000  # ms -> s
            )
        elif self.is_withdrawal(raw):
            return datetime.fromtimestamp(
                int(raw["successTime"]) / 1000  # ms -> s
            )

    def is_successful(self, raw):
        if self.is_trade(raw):
            return "commission" in raw
        elif self.is_deposit(raw):
            return int(raw["status"]) == 1
        elif self.is_withdrawal(raw):
            return int(raw["status"]) == 6

        return False

    def is_trade(self, raw):
        return "isBuyer" in raw

    def is_deposit(self, raw):
        return "insertTime" in raw

    def is_withdrawal(self, raw):
        return "applyTime" in raw

    def build_exchange(self, exchange_name="binance"):
        return super(BinanceParser, self).build_exchange(exchange_name)
