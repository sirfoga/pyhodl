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

from hal.files.save_as import write_dicts_to_json
from hal.streams.user import UserInput

from pyhodl.apis.prices.utils import get_market_cap, get_price_on_dates
from pyhodl.charts.balances import FiatPlotter
from pyhodl.config import DEFAULT_PATHS, RunMode
from pyhodl.core.models.exchanges import Portfolio
from pyhodl.data.balance import get_balance_file
from pyhodl.data.parsers import build_parser, build_exchanges
from pyhodl.stats.transactions import get_transactions_dates, \
    get_all_exchanges, get_all_coins
from pyhodl.updater.core import Updater
from pyhodl.utils.dates import generate_dates
from pyhodl.utils.misc import num_to_str


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(
        usage="-[mode] -h/--help for full usage"
    )

    # run mode
    parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        help="Run mode",
        choices=[x.value for x in RunMode]
    )

    # path
    parser.add_argument(
        "-p",
        "--path",
        dest="path",
        help="Path to use as input",
        type=str
    )

    # extra options
    parser.add_argument(
        "-t",
        "--tor",
        dest="tor",
        help="Connect to tor via this password (advanced)",
        default=False
    )

    # extra options
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="Increase verbosity"
    )

    return parser


def parse_args(parser):
    """
    :param parser: ArgumentParser
        Object that holds cmd arguments.
    :return: tuple
        Values of arguments.
    """

    args = vars(parser.parse_args())
    options = {
        "run": RunMode(args["mode"]),
        "verbose": args["verbose"],
        "tor": args["tor"],
        "path": args["path"]
    }

    if options["path"] is None and options["run"] in DEFAULT_PATHS:
        options["path"] = DEFAULT_PATHS[options["run"]]  # default path
    elif options["path"] is None:
        raise ValueError(
            "You must pass a path option for '" + args["mode"] + "' mode"
        )

    return options


def update(config_file, verbose):
    """
    :param config_file: str
        Path to config file
    :param verbose: bool
        True iff you want verbose output
    :return: void
        Updates your local transactions and saves results
    """

    driver = Updater(config_file, verbose)
    driver.run()


def plot(input_file, verbose):
    """
    :param input_file: str
        Path to input file
    :param verbose: bool
        True iff you want verbose output
    :return: void
        Shows plots with data parsed from input file
    """

    if verbose:
        print("Getting balances from", input_file)

    parser = build_parser(input_file)
    exchange = parser.build_exchange()
    wallets = exchange.build_wallets().values()
    plotter = FiatPlotter(wallets)
    plotter.plot_buy_sells([wallet for wallet in wallets if
                            wallet.base_currency == "TRX"][0])
    plotter.show("Balances from " + input_file)


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


def download_market_cap(since, until, where_to, verbose):
    """
    :param since: datetime
            Get data since this date
    :param until: datetime
        Get data until this date
    :param where_to: str
        Save data here
    :param verbose: bool
        True iff you want verbose output
    :return: void
        Downloads market cap data and saves results
    """

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
    """
    :param coins: [] of str
        List of coins to fetch
    :param since: datetime
            Get data since this date
    :param until: datetime
        Get data until this date
    :param where_to: str
        Save data here
    :param verbose: bool
        True iff you want verbose output
    :param currency: str
        Currency to get prices on
    :param tor: str or None
        Connect to tor proxy with this password
    :return: void
        Downloads prices and saves results
    """

    if verbose:
        print("Getting historical prices for", len(coins), "coins")

    output_file = os.path.join(where_to, currency.lower() + ".json")
    dates = list(generate_dates(since, until, 12))
    data = get_price_on_dates(coins, currency, dates, tor)
    if data:
        write_dicts_to_json(data, output_file)

    if verbose:
        print("Saved historical prices to", output_file)


def main():
    """
    :return: void
        Parse args and run selected mode
    """

    args = parse_args(create_args())
    run_mode, run_path, tor, verbose = \
        args["run"], args["path"], args["tor"], args["verbose"]

    if run_mode == RunMode.UPDATER:
        update(run_path, verbose)
    elif run_mode == RunMode.PLOTTER:
        plot(run_path, verbose)
    elif run_mode == RunMode.STATS:
        if os.path.isfile(run_path):
            show_exchange_balance(run_path)
        else:
            show_folder_balance(run_path)
    elif run_mode == RunMode.DOWNLOAD_HISTORICAL:
        exchanges = get_all_exchanges()
        dates = get_transactions_dates(exchanges)
        first_transaction, last_transaction = min(dates), max(dates)
        coins = get_all_coins(exchanges)

        download_prices(
            coins, first_transaction, last_transaction, run_path, verbose,
            tor=tor
        )
        download_market_cap(
            first_transaction, last_transaction, run_path, verbose
        )
    else:  # null run mode
        print("You realize you just called `pyhodl` with no meaningful args?")
        print("Run `pyhodl --help` to get a list of options.")


def handle_exception(exc):
    """
    :return: void
        Tries to handle it
    """

    print("[CRITICAL ERROR]:", str(exc).replace("\n", ".") + "!!!")
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
    except Exception as exc:
        handle_exception(exc)


if __name__ == '__main__':
    main()  # todo cli()
