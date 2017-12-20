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


""" Command-line program """

import argparse
import os
from datetime import datetime

from pyhodl.data.parsers import parse_transactions

DATETIME_FORMAT = "%Y-%M-%D_%H:%M:%S"
DATETIME_HUMAN = "[YYYY]-[MM]-[DD]_[HH]:[MM]:[SS]"


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(
        usage="-in <database file> -out <output foler> -since <" +
              DATETIME_HUMAN + "> -until <" + DATETIME_HUMAN +
              "> -h/--help for full usage"
    )

    parser.add_argument("-in", dest="in", help="Transactions file",
                        required=True)
    parser.add_argument("-out", dest="out",
                        help="Output folder",
                        required=False)
    parser.add_argument("-since", dest="since",
                        help="Analyze transactions since this date, format "
                             "should be '" + DATETIME_HUMAN + "'",
                        required=False)
    parser.add_argument("-until", dest="until",
                        help="Analyze transactions until this date, format "
                             "should be '" + DATETIME_HUMAN + "'",
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
    params = {}
    keys = [
        "in", "out", "since", "until"
    ]

    for k in keys:
        params[k] = args.__getattribute__(k)

    if params["since"]:
        params["since"] = datetime.strptime(
            params["since"], DATETIME_FORMAT
        )

    if params["until"]:
        params["until"] = datetime.strptime(
            params["until"], DATETIME_FORMAT
        )

    return params


def check_args(params):
    """
    :param params: dict
        Holds cmd args
    :return: bool
        True iff args parser holds valid set of params
    """

    if not os.path.exists(params["in"]):
        raise ValueError("Input file does not exist!")

    if params["since"] and params["until"] and \
                    params["since"] > params["until"]:
        raise ValueError("<since> date must be before <until> date!")

    return True


def main():
    params = parse_args(create_args())  # TODO: add nice try-catch block
    if check_args(params):
        exchange = parse_transactions(params["in"])
        balance = exchange.get_balance()


if __name__ == '__main__':
    main()
