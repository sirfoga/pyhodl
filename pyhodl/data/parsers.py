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

from .core import CryptoParser, BinanceParser, BitfinexParser, CoinbaseParser, \
    GdaxParser


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
                raw_dict = raw_lst[0]
                if "instant_exchange" in raw_dict:
                    return CoinbaseParser(input_file)
                elif "currency" in raw_dict:
                    return GdaxParser(input_file)
    else:  # list
        raw_item = raw_data[0]
        if "timestamp" in raw_item:
            return BitfinexParser(input_file)
        elif "txId" in raw_item or "isBuyer" in raw_item:
            return BinanceParser(input_file)

    raise ValueError("Cannot identify parser for file", input_file)


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

    parsers = build_parser(input_folder)
    transactions = []
    for parser in parsers:
        transactions += list(parser.get_transactions_list())
    return transactions
