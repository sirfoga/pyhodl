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

from datetime import datetime

import colorama
from colorama import Fore
from hal.streams.pretty_table import pretty_format_table

from pyhodl.config import VALUE_KEY
from pyhodl.core.portfolio import Portfolio
from pyhodl.data.balance import get_balance_file, parse_balance, save_balance
from pyhodl.data.parse.build import build_exchanges
from pyhodl.utils.misc import get_relative_delta, \
    get_relative_percentage, print_balance, num_to_str


class Balance:
    """ Deal with exchanges, wallets balances """

    @staticmethod
    def _pretty_balances(balances, last, color=False):
        """
        :param balances: [] of {}
            List of balances of each coin
        :param last: {}
            Dict with last balance data
        :return: str
            Pretty table with balance data
        """

        table = [
            Balance._pretty_balance(balance, last) for balance in balances
        ]
        if color:
            table = Balance._color_table(table, [5, 6])

        return pretty_format_table(
            [
                "symbol", "balance", "$ value", "$ price per coin", "%",
                "$ delta", "% delta"
            ], table
        )

    @staticmethod
    def _color_table(table, floats, eps=1e-5):
        """
        :param table: [] of []
            Matrix
        :param floats: [] of int
            List of columns. Each one of these columns of row will be painted
        :param eps: float
            Epsilon (used to check very small values)
        :return: [] of []
            Matrix with colored columns
        """

        colorama.init()
        color = []
        for row in table:
            color_row = []
            for i, col in enumerate(row):
                val = col
                if i in floats:
                    try:
                        val = float(val)
                        if val < -eps:
                            val = Fore.RED + str(val) + Fore.RESET
                        elif val > eps:
                            val = Fore.GREEN + str(val) + Fore.RESET
                        else:
                            val = Fore.WHITE + str(val) + Fore.RESET
                    except:
                        pass
                color_row.append(val)
            color.append(color_row)
        return color

    @staticmethod
    def _pretty_balance(balance, last):
        current_val = balance[VALUE_KEY]
        last_val = last[balance["symbol"]][VALUE_KEY] \
            if last and balance["symbol"] in last else None

        return [
            str(balance["symbol"]),
            num_to_str(balance["balance"]),
            num_to_str(balance[VALUE_KEY]),
            num_to_str(balance["price"]),
            num_to_str(balance["percentage"]),
            num_to_str(get_relative_delta(current_val, last_val)),
            num_to_str(get_relative_percentage(current_val, last_val))
        ]

    @staticmethod
    def show_exchange(exchange):
        """
        :param exchange: CryptoExchange
            Exchange to get balance of
        :return: void
            Prints balance of exchange
        """

        print("\nExchange:", exchange.exchange_name.title())

        wallets = exchange.build_wallets()
        portfolio = Portfolio(wallets.values())
        last_file = get_balance_file(exchange.exchange_name)
        last = parse_balance(last_file) if last_file else None
        balances, total_value, last_total, last_time = portfolio.get_balance(
            last)

        if last_file:
            save_balance(balances, last_file, timestamp=datetime.now())
        print(Balance._pretty_balances(balances, last, color=True))
        return total_value, last_total, last_time

    @staticmethod
    def show_from_folder(input_folder):
        """
        :param input_folder: str
            Path to input folder
        :return: void
            Prints balance of wallets found in folder
        """

        exchanges = build_exchanges(input_folder)
        total_value = 0.0
        last_total = 0.0
        last_time = None

        for exchange in exchanges:
            total, last, last_time = Balance.show_exchange(exchange)
            total_value += total
            last_total += last if last else 0.0

        delta = get_relative_delta(total_value, last_total)
        percentage = get_relative_percentage(total_value, last_total)

        print("\n")  # space between single exchanges and total value
        print_balance(total_value, delta, percentage, last_time)
