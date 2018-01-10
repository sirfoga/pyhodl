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


""" Updates exchange transactions """

import os
import threading
from datetime import datetime

from binance.client import Client as BinanceClient
from ccxt import bitfinex as bitfinex_client
from coinbase.wallet.client import Client as CoinbaseClient
from gdax import AuthenticatedClient as GdaxClient

from pyhodl.api.markets.factory import ApiManager
from pyhodl.app import ConfigManager
from pyhodl.config import DATA_FOLDER
from pyhodl.utils.dates import parse_datetime, datetime_to_str, parse_timedelta
from pyhodl.utils.misc import get_actual_class_name
from .markets.binance import BinanceUpdater
from .markets.bitfinex import BitfinexUpdater
from .markets.coinbase import CoinbaseUpdater
from .markets.gdax import GdaxUpdater

UPDATE_CONFIG = os.path.join(
    DATA_FOLDER,
    "config.json"
)


class UpdateManager(ConfigManager):
    """ Manages config for Updater """

    def __init__(self):
        ConfigManager.__init__(self, UPDATE_CONFIG)

        self.last_update = None

    def is_time_to_update(self):
        """
        :return: bool
            True iff time elapsed since last time is too much and need to
            update
        """

        return datetime.now() > self.time_next_update()

    def time_next_update(self):
        """
        :return: datetime
            Time of next scheduled update
        """

        return self.time_last_update() + self.update_interval()

    def time_last_update(self):
        """
        :return: datetime
            Time of last update
        """

        if self.last_update:
            return self.last_update

        try:
            return parse_datetime(self.get("last_update"))
        except:
            return datetime.fromtimestamp(0)  # no record

    def update_interval(self):
        """
        :return: timedelta
            Parse time to wait between 2 consecutive updates
        """

        raw = self.get("interval")
        return parse_timedelta(raw)

    def save_time_update(self):
        """
        :return: void
            Saves last time of update to config file
        """

        self.last_update = datetime.now()
        self.data["last_update"] = datetime_to_str(self.last_update)
        self.save()

    def get_data_folder(self):
        """
        :return: str
            Path to folder where will save data
        """

        try:
            folder = self.get("folder")
            os.stat(folder)
        except:
            folder = DATA_FOLDER

        if not os.path.exists(folder):
            os.makedirs(folder)

        return folder


class Updater:
    """ Updates exchanges local data """

    def __init__(self, config_file, verbose):
        self.manager = UpdateManager()
        self.api_manager = ApiManager(config_file=config_file)
        self.api_updaters = []
        self.verbose = verbose

        self.build_updaters()

    def run(self):
        """
        :return: void
            Updates each client and saves data
        """

        interval = self.manager.update_interval().total_seconds()
        threading.Timer(interval, self.run).start()

        if self.verbose:
            print("Updating local data...")

        for updater in self.api_updaters:
            try:
                updater.update(self.verbose)
            except:
                print("Cannot update", get_actual_class_name(updater))

        self.manager.save_time_update()
        print("Next update:", datetime_to_str(self.manager.time_next_update()))

    def build_updaters(self):
        """
        :return: void
            Authenticates each API client
        """

        for api in self.api_manager.get_all():
            try:
                updater = build_updater(
                    api.get_client(), DATA_FOLDER
                )
                self.api_updaters.append(updater)
                print("Successfully authenticated client",
                      get_actual_class_name(api))
            except:
                print("Cannot authenticate client", get_actual_class_name(api))


def get_updater(api_client):
    """
    :param api_client: ApiClient
        Client to get exchange data
    :return: ExchangeUpdater
        Updates exchange
    """

    if isinstance(api_client, BinanceClient):
        return BinanceUpdater
    elif isinstance(api_client, bitfinex_client):
        return BitfinexUpdater
    elif isinstance(api_client, CoinbaseClient):
        return CoinbaseUpdater
    elif isinstance(api_client, GdaxClient):
        return GdaxUpdater


def build_updater(api_client, data_folder):
    """
    :param api_client: ApiClient
        Client to get exchange data
    :param data_folder: str
        Folder where to save data
    :return: ExchangeUpdater
        Concrete updater
    """

    updater = get_updater(api_client)
    if updater:
        return updater(api_client, data_folder)

    raise ValueError("Cannot infer type of API client")
