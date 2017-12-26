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

from pyhodl.data.core import Parser
from .core import CryptoExchange, Wallet, Balance


class CoinbaseParser(Parser):
    """ Parse transactions from Coinbase exchange """

    def get_raw_list(self):
        """
        :return: [] of {}
            List of transactions. Each transaction is a dict with keys
            directly from input file
        """

        epsilon = 1e-15  # max error
        transactions = super().get_raw_list()
        last_balance = float(transactions[0]["Balance"])
        for i, transaction in enumerate(transactions):
            if i == 0:  # first transaction assumed always completed
                transactions[0]["successful"] = True
            else:
                current_balance = float(transaction["Balance"])
                amount = float(transaction["Amount"])
                if abs(last_balance + amount - current_balance) >= epsilon:
                    transactions[i]["successful"] = False
                else:
                    last_balance = current_balance
                    transactions[i]["successful"] = True

        return transactions

    def get_transactions_list(self, **kwargs):
        transactions = super().get_transactions_list(
            "Timestamp",
            "%Y-%m-%d %H:%M:%S %z",
            ["Balance", "Amount", "Transfer Total",
             "Transfer Fee"]
        )
        for i, transaction in enumerate(transactions):
            transactions[i].has_been_performed(transaction["successful"])
        return transactions


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
            coin_sell = transaction["Transfer Total Currency"]
            coin_fee = transaction["Transfer Fee Currency"]

            if coin_sell not in wallet:  # update sell side
                wallet[coin_sell] = Wallet()
            wallet[coin_sell].remove(transaction["Transfer Total"])

            if coin_buy not in wallet:  # update buy side
                wallet[coin_buy] = Wallet()
            wallet[coin_buy].add(transaction["Amount"])

            if coin_fee not in wallet:  # update fee side
                wallet[coin_fee] = Wallet()
            wallet[coin_fee].remove(transaction["Transfer Fee"])

        return Balance(wallet)
