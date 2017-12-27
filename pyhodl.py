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
import time
import traceback
from enum import Enum

from hal.streams.user import UserInput

from pyhodl.updater import Updater


class RunMode(Enum):
    """ Run as ... """

    UPDATER = 0
    PLOTTER = 1
    STATS = 2


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(
        usage="-[mode] -h/--help for full usage"
    )

    parser.add_argument("-updater", "--update", action="store_true",
                        help="Syncs local data with the transactions from "
                             "your exchanges")
    parser.add_argument("-plotter", "--plot", action="store_true",
                        help="Creates charts of your data")
    parser.add_argument("-stats", "--stats", action="store_true",
                        help="Computes statistics and trends using local data")

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
        return RunMode.UPDATER
    elif args.plot:
        return RunMode.PLOTTER
    elif args.stats:
        return RunMode.STATS
    else:
        raise ValueError("Must choose run mode!")


def main():
    run_mode = parse_args(create_args())
    if run_mode == RunMode.UPDATER:
        driver = Updater()
        driver.run()
    elif run_mode == RunMode.PLOTTER:
        raise ValueError("Not fully implemented!")
    elif run_mode == RunMode.STATS:
        raise ValueError("Not fully implemented!")


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


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()  # debug only handle_exception(e)
