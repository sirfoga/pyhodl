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

from pyhodl.logs import Logger
from pyhodl.utils import handle_rate_limits, get_and_sleep

INT_32_MAX = 2 ** 31 - 1


class ExchangeUpdater(Logger):
    """ Abstract exchange updater """

    def __init__(self, api_client, data_folder, rate_limit=1,
                 rate_limit_wait=60):
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
        self.page_limit = INT_32_MAX

    @abc.abstractmethod
    def get_transactions(self):
        """
        :return: [] of Transaction
            List of transactions found
        """

        self.log("getting transactions")

    def save_data(self):
        """
        :return: void
            Saves transactions to file
        """

        if self.transactions:
            self.log("saving data")
            write_dicts_to_json(self.transactions, self.output_file)

    def update(self, verbose):
        """
        :param verbose: bool
            True iff you want to increase verbosity
        :return: void
            Updates local transaction data and saves results
        """

        self.log("updating local data")
        self.get_transactions()
        self.save_data()
        if verbose:
            print(self.class_name, "Transactions written to", self.output_file)

    @staticmethod
    def build_updater(api_client, data_folder):
        """
        :param api_client: ApiClient
            Client to get exchange data
        :param data_folder: str
            Folder where to save data
        :return: ExchangeUpdater
            Concrete updater
        """

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
        """
        :return: [] of str
            List of symbols (currencies)
        """

        symbols = self.client.get_all_tickers()
        return [
            symbol["symbol"] for symbol in symbols
        ]

    @handle_rate_limits
    def get_deposits(self):
        """
        :return: [] of {}
            List of exchange deposits
        """

        return self.client.get_deposit_history()["depositList"]

    @handle_rate_limits
    def get_withdraw(self):
        """
        :return: [] of {}
            List of exchange withdrawals
        """

        return self.client.get_withdraw_history()["withdrawList"]

    @handle_rate_limits
    def get_all_transactions(self, symbol, from_id=0, page_size=500):
        """
        :return: [] of {}
            List of exchange transactions
        """

        trades = self.client.get_my_trades(symbol=symbol, fromId=from_id)
        for i, _ in enumerate(trades):
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
        """
        :return: [] of {}
            List of all exchange movements (transactions + deposits +
            withdrawals)
        """

        super().get_transactions()
        transactions = get_and_sleep(
            self.get_symbols_list(),
            self.get_all_transactions,
            self.rate,
            "transactions"
        )
        self.transactions = \
            transactions + self.get_deposits() + self.get_withdraw()


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
                "limit": INT_32_MAX
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


class CoinbaseUpdater(ExchangeUpdater):
    """ Updates Coinbase data """

    def __init__(self, api_client, data_folder):
        ExchangeUpdater.__init__(self, api_client, data_folder)
        self.accounts = self.client.get_accounts()["data"]
        self.accounts = {
            account["id"]: account for account in self.accounts
        }  # list -> dict
        self.transactions = {
            account_id: [] for account_id in self.accounts
        }
        self.page_limit = 100  # reduced page limit for coinbase and gdax

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
                for i, _ in enumerate(transactions):
                    transactions[i]["currency"] = account["currency"]

            self.transactions[account_id] = transactions
