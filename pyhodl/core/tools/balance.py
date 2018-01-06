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


""" Analyze and print your balance data """

from pyhodl.core.models.exchanges import Portfolio
from pyhodl.data.balance import get_balance_file
from pyhodl.data.parse.build import build_exchanges
from pyhodl.utils.misc import num_to_str


def show_exchange_balance(exchange):
    """
    :param exchange: CryptoExchange
        Exchange to get balance of
    :return: void
        Prints balance of exchange
    """

    print("\nExchange:", exchange.exchange_name.title())

    wallets = exchange.build_wallets()
    portfolio = Portfolio(wallets.values())
    last_balance = get_balance_file(exchange.exchange_name)
    save_to = last_balance
    return portfolio.show_balance(last_balance, save_to)


def show_folder_balance(input_folder):
    """
    :param input_folder: str
        Path to input folder
    :return: void
        Prints balance of wallets found in folder
    """

    exchanges = build_exchanges(input_folder)
    total_value = 0.0
    last_total = 0.0

    for exchange in exchanges:
        total, last = show_exchange_balance(exchange)
        total_value += total
        last_total += last if last else 0.0

    print("\nTotal value of all exchanges ~", num_to_str(total_value), "$")
