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


""" Coinbase exchange """

from pyhodl.models.core import Wallet, Balance
from .core import CryptoExchange


class Coinbase(CryptoExchange):
    """ Models Coinbase exchange """

    def get_balance(self, since, until):
        transactions = self.get_transactions(since, until)
        transactions = [
            transaction for transaction in transactions if
            transaction.successful
        ]  # just successful transactions
        wallet = {}

        for transaction in transactions:
            coin_buy = transaction["Currency"]

            amount = transaction["Amount"]
            if coin_buy not in wallet:  # update buy side
                wallet[coin_buy] = Wallet(transaction.date)
            if amount < 0:
                wallet[coin_buy].remove(amount, transaction.date)
            else:
                wallet[coin_buy].add(amount, transaction.date)

        return Balance(wallet)
