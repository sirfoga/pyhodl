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


""" Get balances stats """

from pyhodl.data.core import BalanceParser


class BalanceStats(object):
    """ Computes balances stats """

    FIAT_CURRENCIES = ["EUR", "USD"]
    CURRENCY_EQUIV = "value"
    BASE_CURRENCY = "USD"

    def __init__(self, input_file, fiats=FIAT_CURRENCIES,
                 base_currency=BASE_CURRENCY):
        """
        :param input_file: str
            File with balances
        :param fiats: str
            Fiat currencies that can be found in file
        :param base_currency: str
            Base currency (to convert from crypto)
        """

        object.__init__(self)
        self.parser = BalanceParser(input_file)
        self.BASE_CURRENCY = base_currency
        self.FIAT_CURRENCIES = [
            fiat + " (" + self.BASE_CURRENCY + " " + self.CURRENCY_EQUIV + ")"
            for fiat in fiats
        ]
        self.crypto_coins = [
            coin for coin in self.parser.balances[0].keys()
            if coin != "date" and self.BASE_CURRENCY not in coin
        ]

    def get_fiat_balance(self):
        """
        :return: [] of {}
            List of fiat balances per date
        """

        for balance in self.parser.balances:
            yield {
                self.BASE_CURRENCY: sum(
                    balance[fiat] for fiat in self.FIAT_CURRENCIES
                ),
                "date": balance["date"]
            }

    def get_crypto_equiv_balance(self):
        """
        :return: [] of {}
            List of crypto balances (fiat equivalent) per date
        """

        for balance in self.parser.balances:
            amount = 0.0
            for coin in self.crypto_coins:
                coin_equiv = coin + " (" + self.BASE_CURRENCY + " " + self.CURRENCY_EQUIV + ")"
                coin_amount = balance[coin_equiv]
                if str(coin_amount) != "nan":
                    amount += coin_amount

            yield {
                self.BASE_CURRENCY: amount,
                "date": balance["date"]
            }
