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


""" Input/output balance data """

import os
from datetime import datetime

from hal.files.parsers import JSONParser
from hal.files.save_as import write_dicts_to_json

from pyhodl.config import DATA_FOLDER, DATE_TIME_KEY, VALUE_KEY
from pyhodl.core.models.exchanges import Portfolio
from pyhodl.data.parse.build import build_exchanges
from pyhodl.utils.dates import parse_datetime, datetime_to_str
from pyhodl.utils.misc import is_nan, num_to_str


def get_balance_file(exchange):
    """
    :param exchange: str
        Exchange name
    :return: str
        Path to balance file dor exchange
    """

    return os.path.join(
        DATA_FOLDER,
        exchange.title() + "Balance.json"
    )


def parse_balance(input_file):
    """
    :param input_file: str
        Parse balance data from this file
    :return: [] of {}
        List of balanced for each wallet found
    """

    if os.path.exists(input_file):
        content = JSONParser(input_file).get_content()
        content[DATE_TIME_KEY] = parse_datetime(content[DATE_TIME_KEY])
        return content


def save_balance(balances, output_file, timestamp=datetime.now()):
    """
    :param balances: [] of {}
        List of balanced for each wallet
    :param output_file: str
        Path to save data to
    :param timestamp: datetime
        Time of log
    :return: void
        Saves data to file
    """

    balances = [
        balance for balance in balances
        if not is_nan(balance[VALUE_KEY])
    ]  # do not save
    data = {}
    for balance in balances:  # lst -> dict
        data[balance["symbol"]] = balance
    data[DATE_TIME_KEY] = datetime_to_str(timestamp)
    write_dicts_to_json(data, output_file)


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
    for exchange in exchanges:
        exchange_value = show_exchange_balance(exchange)
        total_value += exchange_value
    print("\nTotal value of all exchanges ~", num_to_str(total_value), "$")
