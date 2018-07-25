# !/usr/bin/python3
# coding: utf_8


""" API client core to fetch data """

import abc


class ApiConfig:
    """ Config of API """

    def __init__(self, raw):
        """
        :param raw: {}
            Raw data
        """

        self.raw = raw
        self.key = raw["key"]
        self.secret = raw["secret"]

    @abc.abstractmethod
    def get_client(self):
        """
        :return: ApiClient
            Api client
        """

        return
