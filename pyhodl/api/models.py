# !/usr/bin/python3
# coding: utf_8


""" API markets to fetch data """

from pyhodl.logs import Logger
from pyhodl.utils.network import download_with_tor, download


class AbstractApiClient(Logger):
    """ Simple bare api client """

    def __init__(self, base_url):
        """
        :param base_url: str
            Base url for API calls
        """

        Logger.__init__(self)
        self.base_url = base_url


class TorApiClient:
    """ Access API methods via tor """

    def __init__(self, tor=False):
        self.tor = str(tor) if tor else None  # tor password
        if self.tor:
            print("Handling tor sessions with password:", self.tor)

    def download(self, url):
        """
        :param url: str
            Url to fetch
        :return: response
            Response downloaded with tor
        """

        if self.tor:
            return download_with_tor(url, self.tor, 3)

        return download(url)