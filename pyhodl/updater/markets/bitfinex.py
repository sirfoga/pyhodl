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


""" Updates local Bitfinex data """

from pyhodl.updater.models import ExchangeUpdater, INT_32_MAX
from pyhodl.utils.network import handle_rate_limits, get_and_sleep


class BitfinexUpdater(ExchangeUpdater):
    """ Updates Bitfinex data """

    def get_symbols_list(self):
        """
        :return: [] of str
            List of symbols (markets) in exchange
        """

        currencies = self.client.currencies
        symbols = self.client.symbols
        for i, symbol in enumerate(symbols):
            coins = symbol.split("/")
            symbols[i] = "".join([
                currencies[coin]["id"] for coin in coins
            ])
        return symbols

    def get_currencies_list(self):
        """
        :return: [] of str
            List of currencies in exchange
        """

        currencies = self.client.currencies
        currencies = [
            value["id"] for key, value in currencies.items()
        ]
        return currencies

    def fetch(self, data):
        """
        :param data: {}
            Raw request
        :return: response
            Fetch with client
        """

        return self.client.fetch(
            data["url"], headers=data["headers"], body=data["body"]
        )

    @handle_rate_limits
    def get_all_movements(self, symbol):
        """
        :param symbol: str
            Symbol to fetch
        :return: [] of {}
            List of deposits/withdrawals with symbol
        """

        data = self.client.sign(
            "history/movements",
            api="private",
            params={
                "currency": symbol,
                "limit": self.page_limit
            }
        )
        return self.fetch(data)

    def get_movements(self):
        """
        :return: [] of {}
            List of deposits and withdrawals
        """

        return get_and_sleep(
            self.get_currencies_list(),
            self.get_all_movements,
            self.rate,
            "movements"
        )

    @handle_rate_limits
    def get_all_transactions(self, symbol):
        """
        :param symbol: str
            Symbol to fetch
        :return: [] of {}
            List of transactions with symbol
        """

        data = self.client.sign(
            "mytrades",
            api="private",
            params={
                "symbol": symbol,
                "limit_trades": INT_32_MAX
            }
        )
        trades = self.fetch(data)
        for i, _ in enumerate(trades):
            trades[i]["symbol"] = symbol
        return trades

    def get_transactions(self):
        super().get_transactions()
        self.log(
            "Total current balance:",
            [
                (key, val) for key, val
                in self.client.fetch_balance()["total"].items()
            ]
        )

        transactions = get_and_sleep(
            self.get_symbols_list(),
            self.get_all_transactions,
            self.rate,
            "transactions"
        )
        self.transactions = transactions + self.get_movements()
