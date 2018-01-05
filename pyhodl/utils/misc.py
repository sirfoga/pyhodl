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


""" Tools """

import functools
import time
from collections import Counter

import numpy as np
import requests
from hal.internet.web import get_tor_session, renew_connection


def get_full_lists(big_dict):
    """
    :param big_dict: {}
        Dict of similar dicts with varying keys
    :return: {} of {}
        Big dict of dicts with same keys (the dates).
    """

    big_counter = Counter()
    for key, inner_dict in big_dict.items():
        big_counter += inner_dict
    all_keys = big_counter.keys()
    return {
        key: {
            inner_key: inner_value[key] if key in inner_value else None
            for inner_key, inner_value in big_dict.items()
        } for key in all_keys
    }


def get_actual_class_name(class_name):
    """
    :param class_name: str
        Class name of object
    :return: str
        Actual class name (without all path)
    """

    return str(type(class_name)).split("'")[-2].split(".")[-1]


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


def callable_to_str(func, args, kwargs):
    """
    :param func: callback function
        Function to wrap
    :param args: *
        args for callback function
    :param kwargs: **
        kwargs for callback function
    :return: str
        Name of function
    """

    return str(func.__name__) + "(" + str(args) + "," + str(kwargs) + ")"


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


def replace_items(lst, old, new):
    """
    :param lst: []
        List of items
    :param old: obj
        Object to substitute
    :param new: obj
        New object to put in place
    :return: []
        List of items
    """

    for i, val in enumerate(lst):
        if val == old:
            lst[i] = new
    return lst


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


def normalize(val, min_val, max_val, min_range=-1.0, max_range=1.0):
    """
    :param val: float
        Value to normalize
    :param min_val: float
        Min value of value
    :param max_val: float
        Msx value of value
    :param min_range: float
        Min value of range
    :param max_range: float
        Max value of value
    :return: float
        Normalized var in range
    """

    if val >= max_val:
        return max_range

    if val <= min_range:
        return min_range

    ratio = (val - min_val) / (max_val - min_val)
    return min_range + ratio * (max_range - min_range)


def middle(lst):
    """
    :param lst: [] of *
        List
    :return: *
        Object in the middle. In case of ambiguity, take the first one
    """

    middle_point = len(lst) / 2
    return lst[middle_point]


def is_nan(candidate):
    """
    :param candidate: float, str
        Candidate to check
    :return: bool
        True iff is considered NotANumber
    """

    return str(candidate) == "nan"


def remove_same_coordinates(x_data, y_val):
    """
    :param x_data: [] of *
        List of data on x-axis
    :param y_val: [] of float
        List of values
    :return: tuple ([] of *, [] of float)
        Original list minus the points with same x-coordinate
    """

    coordinates = {}
    for x_coord, y_coord in zip(x_data, y_val):
        if x_coord not in coordinates:  # not already in
            coordinates[x_coord] = [y_coord]
        else:  # there was another point
            coordinates[x_coord].append(y_coord)  # create bucket

    for x_coord, y_coord in coordinates.items():  # manage buckets
        coordinates[x_coord] = np.average(y_coord)  # average of bucket

    return list(coordinates.keys()), list(coordinates.values())


def num_to_str(num, form="short"):
    """
    :param num: float
        Number to convert to string
    :param form: str
        Format to use. Must be in ["short", "long"]
    :return: str
        Convert to str using the specified format
    """

    form = SHORT_DEC_FORMAT if form == "short" else LONG_DEC_FORMAT
    return form.format(num)


def do_any_are_in(candidates, bucket):
    """
    :param candidates: [] of *
        List of objects
    :param bucket: [] of *
        List of objects
    :return: bool
        True iff any object of the first list is in bucket
    """

    for candidate in candidates:
        if candidate in bucket:
            return True
    return False


LONG_DEC_FORMAT = "{0:.5f}"
SHORT_DEC_FORMAT = "{0:.3f}"
