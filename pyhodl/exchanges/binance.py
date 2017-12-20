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


""" Binance exchange """

from pyhodl.data.core import Parser
from .core import CryptoExchange, Wallet


class BinanceParser(Parser):
    """ Parse transactions from Binance exchange """

    def get_transactions_list(self, **kwargs):
        return super().get_transactions_list(
            "Date",
            "%Y-%m-%d %H:%M:%S",
            ["Price", "Amount", "Fee", "Total"]
        )


class Binance(CryptoExchange):
    """ Models Binance exchange """

    def get_balance(self, since, until):
        """
        :param since: datetime
            Get transactions done since this date
        :param until: datetime
            Get transactions done until this date
        :return: {} of Wallet
            List of wallets for each coin
        """

        transactions = self.get_transactions(since, until)
        wallet = {}
        for transaction in transactions:
            coin_sell = transaction["Fee Coin"]
            coin_buy = transaction["Market"].replace(coin_sell, "")
            if transaction["Type"] == "SELL":  # other way around
                coin_buy, coin_sell = coin_sell, coin_buy

            if coin_sell not in wallet:  # update sell side
                wallet[coin_sell] = Wallet()
            wallet[coin_sell].remove(transaction["Total"])

            if coin_buy not in wallet:  # update buy side
                wallet[coin_buy] = Wallet()
            wallet[coin_buy].add(transaction["Amount"])
            wallet[coin_buy].remove(transaction["Fee"])
        return wallet
