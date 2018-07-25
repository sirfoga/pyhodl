# !/usr/bin/python3
# coding: utf_8


""" Get transactions stats """

from pyhodl.data.parse.build import build_exchanges
from pyhodl.updater.core import UpdateManager


def get_transactions_dates(items):
    """
    :param items: Exchange, Wallet ...
        Anything with 'transactions' attr
    :return: sorted [] of datetime
        Sorted list of date and time of all transactions in list
    """

    dates = []
    for item in items:
        dates += [
            transaction.date for transaction in item.transactions
        ]
    return sorted(dates)


def get_all_coins(exchanges):
    """
    :param exchanges: [] of CryptoExchange
        List of exchanges
    :return: [] of str
        List of coins in all exchanges
    """

    return list(set([
        coin for exchange in exchanges
        for coin in exchange.build_wallets().keys()
    ]))


def get_all_exchanges():
    """
    :return: [] of CryptoExchange
        List of exchange found in data folder
    """

    folder_in = UpdateManager().get_data_folder()
    return list(build_exchanges(folder_in))
