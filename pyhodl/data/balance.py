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

from pyhodl.config import DATA_FOLDER, DATE_TIME_KEY
from pyhodl.utils import datetime_to_str, parse_datetime


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
        if str(balance["value"]) != "nan"
    ]  # do not save
    data = {}
    for balance in balances:  # lst -> dict
        data[balance["symbol"]] = balance
    data[DATE_TIME_KEY] = datetime_to_str(timestamp)
    write_dicts_to_json(data, output_file)
