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
from .core import CryptoExchange, Wallet, Balance


def infer_coins(transaction):
    """
    :param transaction: Transaction
        Transaction
    :return: tuple (str, str, str, float, float, float)
        Buy coin, sell coin, fee coin, buy amount, sell amount, fee amount
    """

    market = transaction["Market"]
    coin_fee = transaction["Fee Coin"]
    is_sell = transaction["Type"] == "SELL"
    buy_amount = transaction["Total"] if is_sell else transaction["Amount"]
    sell_amount = transaction["Amount"] if is_sell else transaction["Total"]
    fee_amount = transaction["Fee"]

    if market.endswith("USDT"):
        coin_sell = "USDT"
        coin_buy = market.replace(coin_sell, "")
    else:
        coin_buy, coin_sell = market[:3], market[3:]

    if is_sell:  # other way around
        coin_buy, coin_sell = coin_sell, coin_buy

    return coin_buy, coin_sell, coin_fee, buy_amount, sell_amount, fee_amount


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
        transactions = self.get_transactions(since, until)
        wallet = {}
        for transaction in transactions:
            coin_buy, coin_sell, coin_fee, buy_amount, sell_amount, fee_amount \
                = infer_coins(transaction)

            if coin_sell not in wallet:  # update sell side
                wallet[coin_sell] = Wallet()
            wallet[coin_sell].remove(sell_amount)

            if coin_buy not in wallet:  # update buy side
                wallet[coin_buy] = Wallet()
            wallet[coin_buy].add(buy_amount)

            if coin_fee not in wallet:  # update fee side
                wallet[coin_fee] = Wallet()
            wallet[coin_fee].remove(fee_amount)

        return Balance(wallet)
