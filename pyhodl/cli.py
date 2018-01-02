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

import optparse
import os
import time
import traceback
from datetime import timedelta, datetime
from enum import Enum

from hal.files.save_as import write_dicts_to_json
from hal.streams.pretty_table import pretty_format_table
from hal.streams.user import UserInput

from pyhodl.apis.exchanges import API_CONFIG
from pyhodl.apis.prices import get_market_cap, get_prices
from pyhodl.charts.balances import OtherCurrencyPlotter
from pyhodl.config import DATA_FOLDER, HISTORICAL_DATA_FOLDER
from pyhodl.data.parsers import build_parser, build_exchanges
from pyhodl.models.exchanges import Portfolio
from pyhodl.stats.transactions import get_transactions_dates, \
    get_all_exchanges, get_all_coins
from pyhodl.updater.core import Updater


class RunMode(Enum):
    """ Run as ... """

    PLOTTER = "plotter"
    STATS = "stats"
    DOWNLOAD_HISTORICAL = "download"
    UPDATER = "update"


DEFAULT_PATHS = {
    RunMode.STATS: DATA_FOLDER,
    RunMode.DOWNLOAD_HISTORICAL: HISTORICAL_DATA_FOLDER,
    RunMode.UPDATER: API_CONFIG
}


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = optparse.OptionParser(
        usage="-[mode] -h/--help for full usage"
    )

    # run mode
    parser.add_option(
        "-m",
        "--mode",
        dest="mode",
        help="Run mode",
        choices=[x.value for x in RunMode]
    )

    # path
    parser.add_option(
        "-p",
        "--path",
        dest="path",
        help="Path to use as input",
        type=str
    )

    # extra options
    parser.add_option(
        "-t",
        "--tor",
        dest="tor",
        help="Connect to tor via this password (advanced)",
        default=False
    )

    # extra options
    parser.add_option(
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

    args = parser.parse_args()[0].__dict__
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
    driver = Updater(config_file, verbose)
    driver.run()


def plot(input_file, verbose):
    if verbose:
        print("Getting balances from", input_file)

    parser = build_parser(input_file)
    exchange = parser.build_exchange()
    wallets = exchange.build_wallets().values()
    plotter = OtherCurrencyPlotter(wallets)
    plotter.plot_total_balances()
    plotter.show("Balances from " + input_file)


def show_exchange_balance(exchange):
    print("\n\nExchange:", exchange.exchange_name.title())

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
        exchange_value = show_exchange_balance(exchange)
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
            coins, first_transaction, last_transaction, run_path, verbose, tor
        )
        download_market_cap(
            first_transaction, last_transaction, run_path, verbose
        )
    else:  # null run mode
        print("You realize you just called `pyhodl` with no meaningful args?")
        print("Run `pyhodl --help` to get a list of options.")


def handle_exception(e):
    """
    :return: void
        Tries to handle it
    """

    print("[CRITICAL ERROR]:", str(e).replace("\n", ".") + "!!!")
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
        handle_exception(e)


if __name__ == '__main__':
    main()  # todo cli()
