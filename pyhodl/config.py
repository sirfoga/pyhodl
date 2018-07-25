# !/usr/bin/python3
# coding: utf_8


""" App global configs and vars """

import os
from enum import Enum


class RunMode(Enum):
    """ Run as ... """

    PLOTTER = "plotter"
    STATS = "stats"
    DOWNLOAD_HISTORICAL = "download"
    UPDATER = "update"


APP_NAME = "Pyhodl"
APP_SHORT_NAME = "pyhodl"

THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))
HOME_FOLDER = os.getenv("HOME")
APP_FOLDER = os.path.join(
    HOME_FOLDER,
    "." + APP_SHORT_NAME
)
API_FOLDER = os.path.join(
    APP_FOLDER,
    "api"
)
API_CONFIG = os.path.join(
    API_FOLDER,
    "config.json"
)

DATA_FOLDER = os.path.join(
    APP_FOLDER,
    "data"
)
HISTORICAL_DATA_FOLDER = os.path.join(
    APP_FOLDER,
    "historical"
)

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S %z"
DATE_TIME_KEY = "datetime"
VALUE_KEY = "val"
INFINITY = float("inf")
NAN = float("nan")
RAW_DATA_FOLDER = os.path.join(
    THIS_FOLDER,
    "data",
    "raw"
)
COINS_DATABASE = os.path.join(
    RAW_DATA_FOLDER,
    "coins.json"
)

DEFAULT_PATHS = {
    RunMode.STATS: DATA_FOLDER,
    RunMode.DOWNLOAD_HISTORICAL: HISTORICAL_DATA_FOLDER,
    RunMode.UPDATER: API_CONFIG
}


def get_coin_historical_data_file(currency):
    """
    :param currency: str
        Currency to get
    :return: str
        Path to file containing currency historical data
    """

    return os.path.join(HISTORICAL_DATA_FOLDER, currency.lower() + ".json")


# times
SECONDS_IN_MIN = 60
SECONDS_IN_HOUR = 60 * SECONDS_IN_MIN
