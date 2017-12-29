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

from .core import CryptoParser
from ..exchanges.binance import BinanceParser, Binance
from ..exchanges.bitfinex import BitfinexParser, Bitfinex
from ..exchanges.coinbase import CoinbaseParser, Coinbase
from ..exchanges.gdax import GdaxParser, Gdax


def parse_transactions(input_file):
        """
        :param input_file: str
            File to parse
        :return: CryptoExchange
            Builds exchange model based on transactions
        """

        parser = CryptoParser(input_file)
        transaction_attrs = parser.get_raw_data().keys()
        if "Coinbase" in parser.filename:
            return Coinbase(
                CoinbaseParser(input_file).get_transactions_list()
            )
        elif "amount/balance unit" in transaction_attrs:
            return Gdax(
                GdaxParser(input_file).get_transactions_list()
            )
        elif ("Created" in transaction_attrs and "Updated" in
            transaction_attrs) or ("FeeCurrency" in transaction_attrs):
            return Bitfinex(
                BitfinexParser(input_file).get_transactions_list()
            )
        elif parser.is_excel or ("Fee Coin" and "Market" in transaction_attrs):
            return Binance(
                BinanceParser(input_file).get_transactions_list()
            )
        else:
            raise ValueError("Cannot infer type of exchange!")


def parse_transactions_folder(input_folder):
    """
    :param input_folder: str
        Path to folder where to look for transactions files
    :return: [] of CryptoExchange
        Exchanges found (with transactions)
    """

    exchanges = {}
    files = [
        doc for doc in ls_recurse(input_folder) if is_file(doc)
    ]
    for input_file in files:
        try:
            exchange = parse_transactions(input_file)
            exchange_name = str(type(exchange))
            if exchange_name not in exchanges:
                exchanges[exchange_name] = [
                    exchange
                ]
            else:
                exchanges[exchange_name].append(exchange)
        except Exception as e:
            print("Cannot parse input file", input_file)
            print(e)

    return {
        exchange_name: merge_exchanges(exchanges_list)
        for exchange_name, exchanges_list in exchanges.items()
    }.values()
