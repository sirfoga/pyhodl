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


""" Updates exchanges data """

import abc
import os

from binance.client import Client as BinanceClient
from ccxt import bitfinex as BitfinexClient
from coinbase.wallet.client import Client as CoinbaseClient
from gdax.authenticated_client import AuthenticatedClient as GdaxClient
from hal.files.save_as import write_dicts_to_json

from pyhodl.utils import get_actual_class_name

INT_32_MAX = 2 ** 31 - 1


class ExchangeUpdater:
    """ Abstract exchange updater """

    def __init__(self, api_client, data_folder):
        self.client = api_client
        self.folder = data_folder
        self.output_file = os.path.join(
            self.folder,
            get_actual_class_name(self)
        )
        self.transactions = {}

    @abc.abstractmethod
    def get_transactions(self):
        return

    def save_data(self):
        write_dicts_to_json(self.transactions, self.output_file)

    def update(self):
        self.get_transactions()
        self.save_data()

    @staticmethod
    def build_updater(api_client, data_folder):
        if type(api_client) == type(BinanceClient):
            return BinanceUpdater(api_client, data_folder)
        elif type(api_client) == type(BitfinexClient):
            return BitfinexUpdater(api_client, data_folder)
        elif type(api_client) == type(CoinbaseClient):
            return CoinbaseUpdater(api_client, data_folder)
        elif type(api_client) == type(GdaxClient):
            return GdaxUpdater(api_client, data_folder)


class BinanceUpdater(ExchangeUpdater):
    """ Updates Binance data """

    def get_symbols_list(self):
        symbols = self.client.get_all_tickers()
        return [
            symbol["symbol"] for symbol in symbols
        ]

    def get_deposits(self):
        return self.client.get_deposit_history()["depositList"]

    def get_withdraw(self):
        return self.client.get_withdraw_history()["withdrawList"]

    def get_all_transactions(self, symbol, from_id=0, page_size=500):
        trades = self.client.get_my_trades(symbol=symbol, fromId=from_id)
        for i, trade in enumerate(trades):
            trades[i]["symbol"] = symbol

        if trades:  # if page returns some trades, search for others
            last_id = trades[-1]["id"]
            next_id = last_id + page_size + 1
            new_trades = self.get_all_transactions(
                symbol=symbol, from_id=next_id
            )
            if new_trades:
                trades += new_trades

        return trades

    def get_transactions(self):
        transactions = self.get_deposits() + self.get_withdraw()  # deposits
        symbols = self.get_symbols_list()

        for symbol in symbols:  # scan all symbols
            transactions += self.get_all_transactions(symbol)

        return transactions


class BitfinexUpdater(ExchangeUpdater):
    """ Updates Bitfinex data """

    def get_symbols_list(self):
        currencies = self.client.currencies
        symbols = self.client.symbols
        for i, symbol in enumerate(symbols):
            coins = symbol.split("/")
            symbols[i] = "".join([
                currencies[coin]["id"] for coin in coins
            ])
        return symbols

    def get_currencies_list(self):
        currencies = self.client.currencies
        currencies = [
            value["id"] for key, value in currencies.items()
        ]
        return currencies

    def get_all_movements(self, symbol):
        data = self.client.sign(
            "history/movements",
            api="private",
            params={
                "currency": symbol,
                "limit": INT_32_MAX
            }
        )
        return self.client.fetch(
            data["url"], headers=data["headers"], body=data["body"]
        )

    def get_movements(self):
        currencies = self.get_currencies_list()
        movements = []
        for currency in currencies:
            movements += self.get_all_movements(currency)
        return movements

    def get_all_transactions(self, symbol):
        data = self.client.sign(
            "mytrades",
            api="private",
            params={
                "symbol": symbol,
                "limit_trades": INT_32_MAX
            }
        )
        return self.client.fetch(
            data["url"], headers=data["headers"], body=data["body"]
        )

    def get_transactions(self):
        transactions = self.get_movements()  # deposits and withdrawals
        symbols = self.get_symbols_list()

        for symbol in symbols:  # scan all symbols
            transactions += self.get_all_transactions(symbol)

        return transactions


class CoinbaseUpdater(ExchangeUpdater):
    """ Updates Coinbase data """

    def __init__(self, api_client, data_folder):
        ExchangeUpdater.__init__(self, api_client, data_folder)

        self.accounts = self.client.get_accounts()["data"]
        self.transactions = {
            account["id"]: [] for account in self.accounts
        }

    def get_transactions(self):
        for account_id in self.transactions:
            self.transactions[account_id] = \
                self.client.get_transactions(account_id)["data"]


class GdaxUpdater(ExchangeUpdater):
    """ Updates Gdax data """

    def __init__(self, api_client, data_folder):
        ExchangeUpdater.__init__(self, api_client, data_folder)

        self.accounts = self.client.get_accounts()
        self.transactions = {
            account["id"]: [] for account in self.accounts
        }

    def get_transactions(self):
        for account_id in self.transactions:
            pages = self.client.get_account_history(account_id)  # paginated
            transactions = []
            for page in pages:
                transactions += page

            self.transactions[account_id] = transactions
