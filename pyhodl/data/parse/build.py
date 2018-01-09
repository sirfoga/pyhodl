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


""" Parse raw data """

from hal.files.models.system import ls_recurse, is_file
from pyhodl.data.parse.markets.binance import BinanceParser
from pyhodl.data.parse.markets.bitfinex import BitfinexParser
from pyhodl.data.parse.markets.coinbase import CoinbaseParser
from pyhodl.data.parse.markets.gdax import GdaxParser

from pyhodl.data.parse.core import CryptoParser


def build_parser(input_file):
    """
    :param input_file: str
        File to parse
    :return: CryptoExchange
        Builds exchange model based on transactions
    """

    parser = CryptoParser(input_file)
    raw_data = parser.get_raw_data()

    if isinstance(raw_data, dict):  # dict
        for _, raw_lst in raw_data.items():
            if raw_lst:
                raw_data = raw_lst

    parser = get_parser(raw_data)

    if parser:
        return parser(input_file)
    raise ValueError("Cannot identify parser for file", input_file)


def get_parser(raw_data):
    """
    :param raw_data: []
        Raw data
    :return: CryptoParser
        Build parse from raw data
    """

    raw_item = raw_data[0]
    if "instant_exchange" in raw_item:
        return CoinbaseParser
    elif "currency" in raw_item:
        return GdaxParser
    elif "timestamp" in raw_item:
        return BitfinexParser
    elif "txId" in raw_item or "isBuyer" in raw_item:
        return BinanceParser


def build_parsers(input_folder):
    """
    :param input_folder: str
        Path to folder where to look for transactions files
    :return: [] of Parsers
        Parsers found for each file
    """

    files = [
        doc for doc in ls_recurse(input_folder) if is_file(doc)
    ]

    for input_file in files:
        try:
            yield build_parser(input_file)
        except:
            pass


def build_exchanges(input_folder):
    """
    :param input_folder: str
        Path to folder where to look for transactions files
    :return: [] of CryptoExchange
        Exchanges found (with transactions)
    """

    parsers = build_parsers(input_folder)
    for parser in parsers:
        yield parser.build_exchange()


def get_transactions(input_folder):
    """
    :param input_folder: str
        Path to folder where to look for transactions files
    :return: [] of Transaction
        Transactions found in all files from folder
    """

    parsers = build_parsers(input_folder)
    transactions = []
    for parser in parsers:
        transactions += list(parser.get_transactions_list())
    return transactions
