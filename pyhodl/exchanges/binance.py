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

from pyhodl.data.core import CryptoParser
from pyhodl.models.core import Wallet
from .core import CryptoExchange, Balance


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


class BinanceParser(CryptoParser):
    """ Parse transactions from Binance exchange """

    def get_transactions_list(self, **kwargs):
        if self.is_deposit_history() or self.is_withdrawal_history():
            number_keys = ["Amount"]
        else:
            number_keys = ["Price", "Amount", "Fee", "Total"]

        return super().get_transactions_list(
            "Date",
            "%Y-%m-%d %H:%M:%S",
            number_keys
        )


class Binance(CryptoExchange):
    """ Models Binance exchange """

    def get_balance(self, since, until):
        transactions = self.get_transactions(since, until)
        wallet = {}

        for transaction in transactions:
            if transaction.is_deposit() or transaction.is_withdrawal():
                coin = transaction["Coin"]
                amount = transaction["Amount"]
                is_successful = transaction["Status"] == "Completed"

                if is_successful:
                    if coin not in wallet:
                        wallet[coin] = Wallet(transaction.date)

                    if transaction.is_deposit():
                        wallet[coin].add(amount, transaction.date)
                    elif transaction.is_withdrawal():
                        wallet[coin].remove(amount, transaction.date)
                    else:
                        pass
            else:
                coin_buy, coin_sell, coin_fee, buy_amount, sell_amount, fee_amount \
                    = infer_coins(transaction)

                if coin_sell not in wallet:  # update sell side
                    wallet[coin_sell] = Wallet(transaction.date)
                wallet[coin_sell].remove(sell_amount, transaction.date)

                if coin_buy not in wallet:  # update buy side
                    wallet[coin_buy] = Wallet(transaction.date)
                wallet[coin_buy].add(buy_amount, transaction.date)

                if coin_fee not in wallet:  # update fee side
                    wallet[coin_fee] = Wallet(transaction.date)
                wallet[coin_fee].remove(fee_amount, transaction.date)

        return Balance(wallet)
