# !/usr/bin/python3
# coding: utf_8


""" Input/output balance data """

import os
from datetime import datetime

from hal.files.parsers import JSONParser
from hal.files.save_as import write_dicts_to_json

from pyhodl.config import DATA_FOLDER, DATE_TIME_KEY, VALUE_KEY
from pyhodl.utils.dates import parse_datetime, datetime_to_str
from pyhodl.utils.misc import is_nan


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
