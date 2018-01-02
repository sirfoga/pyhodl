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


""" Command-line interface to pyhodl """

import argparse
import os
import time
import traceback
from datetime import timedelta, datetime
from enum import Enum

from hal.files.save_as import write_dicts_to_json
from hal.streams.pretty_table import pretty_format_table
from hal.streams.user import UserInput

from pyhodl.apis.prices import get_market_cap, get_prices
from pyhodl.charts.balances import BalancePlotter
from pyhodl.config import DATA_FOLDER
from pyhodl.data.parsers import build_parser, build_exchanges
from pyhodl.models.exchanges import Portfolio
from pyhodl.stats.transactions import get_transactions_dates, \
    get_all_exchanges, get_all_coins
from pyhodl.updater.core import Updater


class RunMode(Enum):
    """ Run as ... """

    UPDATER = 0
    PLOTTER = 1
    STATS = 2
    DOWNLOAD_HISTORICAL = 3


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(
        usage="-[mode] -h/--help for full usage"
    )

    parser.add_argument("-update", "--update", action="store_true",
                        help="Syncs local data with the transactions from "
                             "your exchanges")
    parser.add_argument("-hist", dest="hist",
                        help="Downloads historical prices of your coins",
                        required=False)
    parser.add_argument("-plot", dest="plot",
                        help="Creates charts of your data",
                        required=False)
    parser.add_argument("-stats", "--stats", action="store_true",
                        help="Computes"
                             "statistics and trends using local data")
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="Increase verbosity")
    parser.add_argument("-tor", dest="tor",
                        help="Connect to tor via this password (advanced)",
                        required=False)

    return parser


def parse_args(parser):
    """
    :param parser: ArgumentParser
        Object that holds cmd arguments.
    :return: tuple
        Values of arguments.
    """

    args = parser.parse_args()

    if args.update:
        return RunMode.UPDATER, args.verbose
    elif args.plot:
        return RunMode.PLOTTER, os.path.join(args.plot), args.verbose
    elif args.stats:
        return RunMode.STATS, DATA_FOLDER, args.verbose
    elif args.hist:
        return RunMode.DOWNLOAD_HISTORICAL, \
               os.path.join(args.hist), args.verbose, args.tor

    raise ValueError("Invalid run mode!")


def update(verbose):
    driver = Updater(verbose)
    driver.run()


def plot(input_file, verbose):
    if verbose:
        print("Getting balances from", input_file)

    parser = build_parser(input_file)
    exchange = parser.build_exchange()
    wallets = exchange.build_wallets()
    plotter = BalancePlotter(wallets.values())
    plotter.plot_balances()
    plotter.show("Balances from " + input_file)


def show_exchange_balance(exchange, verbose):
    if verbose:
        print("\n\nPrinting balances of", exchange.exchange_name)

    wallets = exchange.build_wallets()
    portfolio = Portfolio(wallets.values())
    table, tot_balance = portfolio.get_current_balance()
    pretty_table = pretty_format_table(
        ["symbol", "balance", "$ value", "$ price per coin"],
        table
    )

    print("As of", datetime.now(), "you got")
    print(pretty_table)
    print("Total value: ~", tot_balance, "$")
    return tot_balance


def show_folder_balance(input_folder):
    exchanges = build_exchanges(input_folder)
    total_value = 0.0
    for exchange in exchanges:
        exchange_value = show_exchange_balance(exchange, True)
        total_value += exchange_value
    print("Total value of all exchanges ~", total_value, "$")


def download_market_cap(since, until, where_to, verbose):
    if verbose:
        print("Getting market cap since", since, "until", until)

    output_file = os.path.join(where_to, "market_cap.json")
    data = get_market_cap(since, until)
    if data:
        write_dicts_to_json(data, output_file)

    if verbose:
        print("Saved market cap data to", output_file)


def download_prices(coins, since, until, where_to, verbose, currency="USD",
                    tor=False):
    if verbose:
        print("Getting historical prices for", len(coins), "coins")

    output_file = os.path.join(where_to, currency.lower() + ".json")
    extra_time = timedelta(hours=6)
    data = get_prices(
        coins, currency, since - extra_time, until + extra_time, tor
    )
    if data:
        write_dicts_to_json(data, output_file)

    if verbose:
        print("Saved historical prices to", output_file)


def main():
    run_mode, *args = parse_args(create_args())
    if run_mode == RunMode.UPDATER:
        update(args[0])
    elif run_mode == RunMode.PLOTTER:
        plot(args[0], args[1])
    elif run_mode == RunMode.STATS:
        if os.path.isfile(args[0]):
            show_exchange_balance(args[0], args[1])
        elif os.path.isdir(args[0]):
            show_folder_balance(args[0])
        else:
            show_folder_balance(DATA_FOLDER)
    elif run_mode == RunMode.DOWNLOAD_HISTORICAL:
        exchanges = get_all_exchanges()
        dates = get_transactions_dates(exchanges)
        first_transaction, last_transaction = min(dates), max(dates)
        coins = get_all_coins(exchanges)
        download_prices(
            coins, first_transaction, last_transaction, args[0], args[1],
            tor=args[2]
        )

        download_market_cap(
            first_transaction, last_transaction, args[0], args[1]
        )


def handle_exception():
    """
    :return: void
        Tries to handle it
    """

    print("pyhodl stopped abruptly, but your data is safe, don't worry.")
    user_input = UserInput()
    if user_input.get_yes_no("Want to fill a bug report?"):
        print("Please file a bug report here >> "
              "https://github.com/sirfoga/pyhodl/issues attaching the "
              "following content ...")
        time.sleep(1)
        traceback.print_exc()

    print("Terribly sorry for the inconvenience, see you soon!")


def cli():
    """
    :return: void
        Run this as cmd program
    """

    try:
        main()
    except Exception as e:
        traceback.print_exc()  # debug only handle_exception(e)


if __name__ == '__main__':
    cli()
