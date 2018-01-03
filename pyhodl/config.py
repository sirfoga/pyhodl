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


""" App global configs and vars """
import os

from pyhodl.data.coins import Coin, CoinsNamesTable

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
FIAT_COINS = [Coin("USD"), Coin("EUR")]  # supported fiat coins
DEFAULT_FIAT = "USD"
CRYPTO_COINS = CoinsNamesTable(COINS_DATABASE).get_coins()
