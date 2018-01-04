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


""" Utils methods to deal with dates """

import time
from datetime import timedelta, datetime

import pytz

from pyhodl.config import DATE_TIME_FORMAT


def generate_dates(since, until, hours):
    """
    :param since: datetime
        Generate dates since this date
    :param until: datetime
        Generate dates until this date
    :param hours: float
        Number of hours between 2 consecutive dates
    :return: generator of datetime
        Dates in between boundaries and separated by exact interval
    """

    date = since
    while date <= until:
        yield date
        date += timedelta(hours=hours)
    yield until


def datetime_to_unix_timestamp_ms(date_time):
    """
    :param date_time: datetime
        Date and time
    :return: int
        Unix timestamp (milliseconds)
    """

    return int(time.mktime(date_time.timetuple()) * 1e3 +
               date_time.microsecond / 1e3)


def datetime_to_unix_timestamp_s(date_time):
    """
    :param date_time: datetime
        Date and time
    :return: int
        Unix timestamp (seconds)
    """

    return int(time.mktime(date_time.timetuple()) * 1e3)


def unix_timestamp_ms_to_datetime(milliseconds):
    """
    :param milliseconds: int
        Unix timestamp (milliseconds)
    :return: datetime
        Date and time (UTC)
    """

    date_time = datetime.fromtimestamp(float(milliseconds) / 1e3)
    return localize(date_time)  # utc as default time zone


def parse_datetime(raw):
    """
    :param raw: str
        Raw date and time
    :return: datetime
        Datetime
    """

    return datetime.strptime(raw, DATE_TIME_FORMAT)


def datetime_to_str(date_time):
    """
    :param date_time: datetime
        Date and time
    :return: str
        String representation
    """

    if date_time.tzinfo is None:
        date_time = localize(date_time)  # utc as default time zone
    return date_time.strftime(DATE_TIME_FORMAT)


def localize(date_time):
    """
    :param date_time: datetime
        Date and time
    :return: datetime
        UTC-localized date and time (if NOT localized), else original
    """

    if date_time.tzinfo is None:
        return pytz.utc.localize(date_time)

    return date_time


def get_delta_seconds(first, second):
    """
    :param first: datetime
        Date and time
    :param second: datetime
        Date and time to subtract to first
    :return: int
        Total difference in seconds
    """

    return (localize(first) - localize(second)).total_seconds()
