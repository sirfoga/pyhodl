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


""" Deal with network issues """

import functools
import time

import requests
from hal.internet.web import get_tor_session, renew_connection

from .misc import callable_to_str


def handle_rate_limits(func, time_wait=60, max_attempts=2):
    """
    :param func: callback function
        function to wrap
    :param time_wait: int
        Time to wait between consecutive attempts
    :param max_attempts: int
        Max number of attempt to do before giving up
    :return: callback function return type
        wraps callback function
    """

    @functools.wraps(func)
    def _handle_rate_limits(*args, **kwargs):
        """
        :param args: *
            args for callback function
        :param kwargs: **
            kwargs for callback function
        :return: callback function return type
            handle rate limit of callback function
        """

        function_name = callable_to_str(func, args, kwargs)
        attempt_counter = 0

        while attempt_counter < max_attempts:
            try:
                attempt_counter += 1
                return func(*args, **kwargs)
            except Exception as exc:
                if is_network_rate_error(exc):
                    print(
                        function_name,
                        ">>> Attempt #", attempt_counter,
                        ": rate limit exceeded! Wait time:", time_wait,
                        "seconds before next request"
                    )

                    # useless wait if last attempt
                    if attempt_counter + 1 <= max_attempts:
                        time.sleep(time_wait * 1.1)  # extra seconds to be sure
                else:
                    return None  # exception not rate limit related
        return None

    return _handle_rate_limits


def is_network_rate_error(exc):
    """
    :param exc: Exception
        Exception thrown when requesting network resource
    :return: bool
        True iff exception tells you abused APIs
    """

    keys = ["429", "Connection refused"]
    for key in keys:
        if key in str(exc):
            return True
    return False


def get_and_sleep(symbols, fetcher, sleep_time, log_data):
    """
    :param symbols: [] of *
        List of data to fetch
    :param fetcher: func
        Perform operations with this function on each data
    :param sleep_time: int
        After operations, sleep this amount of seconds
    :param log_data: str
        Extra log data to print
    :return: [] of *
        Performs function on each data, waits (after each operation) and
        returns results
    """

    data = []
    for symbol in symbols:  # scan all symbols
        try:
            result = fetcher(symbol)
            data += result
            print("Found", len(result), symbol, log_data)
            time.sleep(sleep_time)
        except:
            print("Cannot get", symbol, log_data)
    return data


def download(url):
    """
    :param url: str
        Url to get
    :return: response
        Response of request
    """

    return requests.get(url)


def download_with_tor(url, tor_password, max_attempts):
    """
    :param url: str
        Url to get
    :param tor_password: str
        Password to connect to tor proxy
    :param max_attempts: int
        Max number of attempts to do
    :return: response
        Response of request
    """

    try:
        session = get_tor_session()
        session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:52.0) "
                          "Gecko/20100101 Firefox/52.0",
            "Cookie": "__cfduid=d87e2b033d4ee407a1c3303b532c32dec1514830829"
        }
        return session.get(url)
    except:
        if max_attempts > 0:
            print("Cannot download", url, "via tor. Trying to renew session.")
            renew_connection(tor_password)
            return download_with_tor(url, tor_password, max_attempts - 1)

        return None
