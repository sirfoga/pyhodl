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


""" Bitfinex exchange """

from pyhodl.data.core import Parser
from .core import CryptoExchange, Wallet, Balance


class BitfinexParser(Parser):
    """ Parse transactions from Bitfinex exchange """

    def get_transactions_list(self, **kwargs):
        if self.is_deposit_history() or self.is_withdrawal_history():
            date_key = "Updated"
            number_keys = ["Amount"]
        else:
            date_key = "Date"
            number_keys = ["Price", "Amount", "Fee"]

        return super().get_transactions_list(
            date_key,
            "%Y-%m-%d %H:%M:%S",
            number_keys
        )


class Bitfinex(CryptoExchange):
    """ Models Bitfinex exchange """

    def get_balance(self, since, until):
        transactions = self.get_transactions(since, until)
        wallet = {}
        for transaction in transactions:
            if transaction.is_deposit() or transaction.is_withdrawal():
                coin = transaction["Currency"]
                amount = transaction["Amount"]
                is_successful = transaction["Status"] == "COMPLETED"

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
                coin_buy, coin_sell = transaction["Pair"].split( \
                    "/")
                coin_fee = transaction["FeeCurrency"]

                if coin_sell not in wallet:  # update sell side
                    wallet[coin_sell] = Wallet(transaction.date)

                sell_amount = transaction["Amount"] * transaction["Price"]
                wallet[coin_sell].remove(sell_amount, transaction.date)

                if coin_buy not in wallet:  # update buy side
                    wallet[coin_buy] = Wallet(transaction.date)
                wallet[coin_buy].add(transaction["Amount"], transaction.date)

                if coin_fee not in wallet:  # update fees
                    wallet[coin_fee] = Wallet(transaction.date)
                wallet[coin_fee].remove(abs(transaction["Fee"]),
                                        transaction.date)

        return Balance(wallet)
