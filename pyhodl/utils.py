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
from datetime import datetime
from datetime import timedelta

import pytz
import requests
from hal.internet.web import get_tor_session, renew_connection

from pyhodl.app import DATE_TIME_FORMAT


def generate_dates(since, until, interval):
    """
    :param since: datetime
        Generate dates since this date
    :param until: datetime
        Generate dates until this date
    :param interval: float
        Number of hours between 2 consecutive dates
    :return: generator of datetime
        Dates in between boundaries and separated by exact interval
    """

    date = since
    while date <= until:
        yield date
        date += timedelta(hours=interval)
    yield until


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

        function_name = str(func.__name__) + "(" + str(args) + "," + str(
            kwargs) + ")"
        attempt_counter = 0

        while attempt_counter < max_attempts:
            try:
                attempt_counter += 1
                return func(*args, **kwargs)
            except Exception as e:
                if "429" in str(e) or "Connection refused" in str(e):
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
        print(
            function_name,
            "max number of attempts:", max_attempts, " reached!"
        )
        return None

    return _handle_rate_limits


def get_dates(first, last, sec_interval):
    """
    :param first: datetime
        Start generating dates since this time
    :param last: datetime
        End generating dates until this time
    :param sec_interval: int
        Number of seconds between 2 consecutive dates
    :return: [] of datetime
        Range of datetimes
    """

    intervals = last - first
    intervals = int(intervals.total_seconds() / sec_interval) + 1
    return [
        first + timedelta(seconds=i * sec_interval)
        for i in range(intervals)
    ]


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


def datetime_to_unix_timestamp_ms(dt):
    return int(time.mktime(dt.timetuple()) * 1e3 + dt.microsecond / 1e3)


def unix_timestamp_ms_to_datetime(ms):
    dt = datetime.fromtimestamp(ms / 1e3)
    return pytz.utc.localize(dt)  # utc as default time zone


def download(url):
    return requests.get(url)


def download_with_tor(url, tor_password, max_attempts):
    try:
        session = get_tor_session()
        return session.get(
            url
        )
    except Exception as e:
        if max_attempts > 0:
            print("Cannot download", url, "via tor due to", e,
                  ". Trying to renew session.")
            renew_connection(tor_password)
            return download_with_tor(url, tor_password, max_attempts - 1)

        return None


def parse_datetime(raw):
    return datetime.strptime(raw, DATE_TIME_FORMAT)


def datetime_to_str(dt):
    return dt.strftime(DATE_TIME_FORMAT)
