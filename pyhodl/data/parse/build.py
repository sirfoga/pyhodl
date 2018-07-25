# !/usr/bin/python3
# coding: utf_8


""" Parse raw data """

from hal.files.models.system import ls_recurse, is_file

from pyhodl.data.parse.core import CryptoParser
from .markets.binance import BinanceParser
from .markets.bitfinex import BitfinexParser
from .markets.coinbase import CoinbaseParser
from .markets.gdax import GdaxParser


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
