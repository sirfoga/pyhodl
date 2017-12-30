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


""" Command-line interface to Pyhodl """

import argparse
import os
import time
import traceback
from datetime import timedelta
from enum import Enum

from hal.files.save_as import write_dicts_to_json
from hal.streams.user import UserInput

from pyhodl.apis.prices import get_price
from pyhodl.data.parsers import build_exchanges
from pyhodl.updater.core import Updater, UpdateManager


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
    parser.add_argument("-plot", "--plot", action="store_true",
                        help="Creates charts of your data")
    parser.add_argument("-stats", "--stats", action="store_true",
                        help="Computes statistics and trends using local data")
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="Increase verbosity")

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
        return RunMode.PLOTTER, args.verbose
    elif args.stats:
        return RunMode.STATS, args.verbose
    elif args.hist:
        return RunMode.DOWNLOAD_HISTORICAL, \
               os.path.join(args.hist), args.verbose

    raise ValueError("Invalid run mode!")


def update(verbose):
    driver = Updater(verbose)
    driver.run()


def plot(verbose):
    raise ValueError("Not fully implemented!")


def compute_stats(verbose):
    raise ValueError("Not fully implemented!")


def download_historical(where_to, verbose, sec_interval=12 * 60 * 60,
                        fiat="USD"):
    folder_in = UpdateManager().get_data_folder()
    exchanges = list(build_exchanges(folder_in))

    first_transaction = min([
        exchange.get_first_transaction() for exchange in exchanges
    ], key=lambda x: x.date)
    last_transaction = max([
        exchange.get_last_transaction() for exchange in exchanges
    ], key=lambda x: x.date)
    intervals = last_transaction.date - first_transaction.date
    intervals = int(intervals.total_seconds() / sec_interval) + 1

    coins = [
        coin for exchange in exchanges
        for coin in exchange.build_wallets().keys()
    ]  # list of dict (str -> Wallet)

    dates = [
        first_transaction.date + timedelta(seconds=i * sec_interval)
        for i in range(intervals)
    ]

    prices = []
    for date in dates:
        try:
            new_prices = get_price(coins, fiat, date)
            new_prices["date"] = date.strftime(
                "%Y-%m-%d %H:%M:%S %z"
            )
            prices.append(new_prices)
            print("Got prices up to", date)
            time.sleep(10)
        except Exception as e:
            print("Failed getting prices for", date, "due to", e)
    write_dicts_to_json(prices, "out.json")


def main():
    run_mode, *args = parse_args(create_args())
    if run_mode == RunMode.UPDATER:
        update(args[0])
    elif run_mode == RunMode.PLOTTER:
        plot(args[0])
    elif run_mode == RunMode.STATS:
        compute_stats(args[0])
    elif run_mode == RunMode.DOWNLOAD_HISTORICAL:
        download_historical(args[0], args[1])


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
