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


""" Get transactions stats """

from datetime import datetime

from hal.streams.pretty_table import pretty_format_table

from pyhodl.app import DATE_TIME_KEY, VALUE_KEY
from pyhodl.data.parsers import build_exchanges


def show_balance_of_exchange(exchange, verbose):
    if verbose:
        print("\n\nPrinting balances of", exchange.exchange_name)

    wallets = exchange.build_wallets()
    balances = [
        {
            "symbol": coin,
            "balance": wallet.balance(),
            "value": wallet.get_balance_equivalent_now()
        }
        for coin, wallet in wallets.items()
    ]
    balances = sorted([
        balance for balance in balances if float(balance["balance"]) > 0.0
    ], key=lambda x: x["value"], reverse=True)
    table = [
        [
            str(balance["symbol"]),
            str(balance["balance"]),
            str(balance["value"]) + " $",
            str(float(balance["value"] / float(balance["balance"]))) + " $"
        ]
        for balance in balances
    ]
    pretty_table = pretty_format_table(
        ["symbol", "balance", "$ value", "$ price per coin"],
        table
    )

    print("As of", datetime.now(), "you got")
    print(pretty_table)
    tot_balance = sum([balance["value"] for balance in balances])
    print("Total value: ~", tot_balance, "$")
    return tot_balance


def show_balance_of_folder(input_folder):
    exchanges = build_exchanges(input_folder)
    total_value = 0.0
    for exchange in exchanges:
        exchange_value = show_balance_of_exchange(exchange, True)
        total_value += exchange_value
    print("Total value of all exchanges ~", total_value, "$")


def get_total_equivalent_balances(wallets, currency):
    """
    :param wallets: [] of Wallet
        List of wallets
    :param currency: str
        Currency to convert to
    :return: [] of {}
        List of dates, currency equivalent of total balance by date
    """

    all_deltas = []
    for wallet in wallets:
        deltas = list(wallet.get_delta_balance_by_transaction())
        equivalents = [
            {
                DATE_TIME_KEY: delta["transaction"].date,
                VALUE_KEY: wallet.get_equivalent(
                    delta["transaction"].date,
                    currency,
                    delta[VALUE_KEY]
                )
            } for delta in deltas
        ]
        all_deltas += equivalents

    all_deltas = sorted(all_deltas, key=lambda x: x[DATE_TIME_KEY])
    all_balances = [all_deltas[0]]
    for delta in all_deltas[1:]:
        all_balances.append({
            DATE_TIME_KEY: delta[DATE_TIME_KEY],
            VALUE_KEY: all_balances[-1][VALUE_KEY] + delta[VALUE_KEY]
        })
    return all_balances
