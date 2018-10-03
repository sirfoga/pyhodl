# !/usr/bin/python3
# coding: utf_8


""" Updates exchanges data """

import abc
import os

from hal.files.save_as import write_dicts_to_json

from pyhodl.logs import Logger

INT_32_MAX = 2 ** 31 - 1


class ExchangeUpdater(Logger):
    """ Abstract exchange updater """

    def __init__(self, api_client, data_folder, rate_limit=1,
                 rate_limit_wait=60):
        """
        :param api_client: ApiClient
            Client with which to perform requests
        :param data_folder: str
            Folder where to save data
        :param rate_limit: int
            Number of seconds between 2 consecutive requests
        :param rate_limit_wait: int
            Number of seconds to wait if rate limit exceeded
        """

        Logger.__init__(self)

        self.client = api_client
        self.folder = data_folder
        self.output_file = os.path.join(
            self.folder,
            self.class_name + ".json"
        )
        self.transactions = {}
        self.rate = float(rate_limit)
        self.rate_wait = float(rate_limit_wait)
        self.page_limit = INT_32_MAX

    @abc.abstractmethod
    def get_transactions(self):
        """
        :return: [] of Transaction
            List of transactions found
        """

        self.log("getting transactions")

    def save_data(self):
        """
        :return: void
            Saves transactions to file
        """

        if self.transactions:
            self.log("saving data")
            write_dicts_to_json(self.transactions, self.output_file)

    def update(self, verbose):
        """
        :param verbose: bool
            True iff you want to increase verbosity
        :return: void
            Updates local transaction data and saves results
        """

        self.log("updating local data")
        self.get_transactions()
        self.save_data()
        if verbose:
            print(self.class_name, "Transactions written to", self.output_file)
