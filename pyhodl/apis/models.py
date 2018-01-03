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


""" API client core to fetch data """

from pyhodl.logs import Logger
from pyhodl.utils.misc import download_with_tor, download


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
