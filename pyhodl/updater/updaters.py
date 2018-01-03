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
import time

from binance.client import Client as BinanceClient
from ccxt import bitfinex as BitfinexClient
from coinbase.wallet.client import Client as CoinbaseClient
from gdax.authenticated_client import AuthenticatedClient as GdaxClient
from hal.files.save_as import write_dicts_to_json

from pyhodl.logs import Logger
from pyhodl.utils import handle_rate_limits

INT_32_MAX = 2 ** 31 - 1


class ExchangeUpdater(Logger):
    """ Abstract exchange updater """

    def __init__(self, api_client, data_folder, rate_limit=1,
                 rate_limit_wait=60, page_limit=INT_32_MAX):
        """
        :param api_client: ApiClient
            Client with which to perform requests
        :param data_folder: str
            Folder where to save data
        :param rate_limit: int
            Number of seconds between 2 consecutive requests
        :param rate_limit_wait: int
            Number of seconds to wait if rate limit exceeded
        :param page_limit: int
            Limit of requests per page
        """

        Logger.__init__(self)
        
        self.client = api_client
        self.folder = data_folder
        self.output_file = os.path.join(
            self.folder,
            self.class_name + ".json"
        )
        self.transactions = {}
        self.rate = float(rate_limit)
        self.rate_wait = float(rate_limit_wait)
        self.page_limit = int(page_limit)

    @abc.abstractmethod
    def get_transactions(self):
        self.log("getting transactions")

    def save_data(self):
        self.log("saving data")
        write_dicts_to_json(self.transactions, self.output_file)

    def update(self, verbose):
        self.log("updating local data")
        self.get_transactions()
        self.save_data()
        if verbose:
            print(self.class_name, "Transactions written to", self.output_file)

    @staticmethod
    def build_updater(api_client, data_folder):
        if isinstance(api_client, BinanceClient):
            return BinanceUpdater(api_client, data_folder)
        elif isinstance(api_client, BitfinexClient):
            return BitfinexUpdater(api_client, data_folder)
        elif isinstance(api_client, CoinbaseClient):
            return CoinbaseUpdater(api_client, data_folder)
        elif isinstance(api_client, GdaxClient):
            return GdaxUpdater(api_client, data_folder)
        else:
            raise ValueError("Cannot infer type of API client")


class BinanceUpdater(ExchangeUpdater):
    """ Updates Binance data """

    def get_symbols_list(self):
        symbols = self.client.get_all_tickers()
        return [
            symbol["symbol"] for symbol in symbols
        ]

    @handle_rate_limits
    def get_deposits(self):
        return self.client.get_deposit_history()["depositList"]

    @handle_rate_limits
    def get_withdraw(self):
        return self.client.get_withdraw_history()["withdrawList"]

    @handle_rate_limits
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
        super().get_transactions()
        transactions = self.get_deposits() + self.get_withdraw()  # deposits
        symbols = self.get_symbols_list()

        for symbol in symbols:  # scan all symbols
            try:
                result = self.get_all_transactions(symbol)
                transactions += result
                self.log("Found", len(result), symbol, "transactions")
                time.sleep(self.rate)
            except:
                self.log("Cannot get", symbol, "transactions")
        self.transactions = transactions


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

    @handle_rate_limits
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
        symbols = self.get_currencies_list()
        movements = []
        for symbol in symbols:
            try:
                result = self.get_all_movements(symbol)
                movements += result
                self.log("Found", len(result), symbol, "movements")
                time.sleep(self.rate)
            except:
                self.log("Cannot get", symbol, "movements")
        return movements

    @handle_rate_limits
    def get_all_transactions(self, symbol):
        data = self.client.sign(
            "mytrades",
            api="private",
            params={
                "symbol": symbol,
                "limit_trades": INT_32_MAX
            }
        )
        trades = self.client.fetch(
            data["url"], headers=data["headers"], body=data["body"]
        )
        for i, trade in enumerate(trades):
            trades[i]["symbol"] = symbol
        return trades

    def get_transactions(self):
        super().get_transactions()
        self.log("Total current balance:",
                 [
                (key, val) for key, val
                in self.client.fetch_balance()["total"].items()
            ]
                 )

        transactions = self.get_movements()  # deposits and withdrawals
        symbols = self.get_symbols_list()
        for symbol in symbols:  # scan all symbols
            try:
                result = self.get_all_transactions(symbol)
                transactions += result
                self.log("Found", len(result), symbol, "transactions")
                time.sleep(self.rate)
            except:
                self.log("Cannot get", symbol, "transactions")
        self.transactions = transactions


class CoinbaseUpdater(ExchangeUpdater):
    """ Updates Coinbase data """

    def __init__(self, api_client, data_folder):
        ExchangeUpdater.__init__(self, api_client, data_folder, page_limit=100)

        self.accounts = self.client.get_accounts()["data"]
        self.accounts = {
            account["id"]: account for account in self.accounts
        }  # list -> dict
        self.transactions = {
            account_id: [] for account_id in self.accounts
        }

    def get_transactions(self):
        super().get_transactions()
        for account_id, account in self.accounts.items():
            self.log("Getting transaction history of account",
                     account["id"], "(" + account["balance"]["currency"] + ")")
            raw_data = self.client.get_transactions(
                account_id,
                limit=self.page_limit
            )
            self.transactions[account_id] += raw_data["data"]

            while "pagination" in raw_data:  # other transactions
                raw_data = self.client.get_transaction(
                    raw_data["pagination"]["previous_uri"]
                )
                self.transactions[account_id] += raw_data["data"]


class GdaxUpdater(ExchangeUpdater):
    """ Updates Gdax data """

    def __init__(self, api_client, data_folder):
        ExchangeUpdater.__init__(self, api_client, data_folder)

        self.accounts = self.client.get_accounts()
        self.accounts = {
            account["id"]: account for account in self.accounts
        }  # list -> dict
        self.transactions = {
            account_id: [] for account_id in self.accounts
        }

    def get_transactions(self):
        super().get_transactions()
        for account_id, account in self.accounts.items():
            self.log("Getting transaction history of account",
                     account["id"], "(" + account["currency"] + ")")
            pages = self.client.get_account_history(account_id)
            transactions = []
            for page in pages:
                transactions += page

            if transactions:  # add currency symbol
                for i, transaction in enumerate(transactions):
                    transactions[i]["currency"] = account["currency"]

            self.transactions[account_id] = transactions
