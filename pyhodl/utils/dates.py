# !/usr/bin/python3
# coding: utf_8


""" Utils methods to deal with dates """

import time
from datetime import timedelta, datetime

import pytz

from pyhodl.config import DATE_TIME_FORMAT, SECONDS_IN_HOUR


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

    seconds = datetime_to_unix_timestamp_s(datetime)
    return int(seconds * 1e3 + date_time.microsecond / 1e3)


def datetime_to_unix_timestamp_s(date_time):
    """
    :param date_time: datetime
        Date and time
    :return: int
        Unix timestamp (seconds)
    """

    return int(time.mktime(date_time.timetuple()))


def unix_timestamp_ms_to_datetime(milliseconds):
    """
    :param milliseconds: int
        Unix timestamp (milliseconds)
    :return: datetime
        Date and time (UTC)
    """

    return unix_timestamp_s_to_datetime(milliseconds / 1e3)


def unix_timestamp_s_to_datetime(seconds):
    """
    :param seconds: int
        Unix timestamp (seconds)
    :return: datetime
        Date and time (UTC)
    """

    date_time = datetime.fromtimestamp(float(seconds))
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


def get_delta_hours(first, second):
    """
    :param first: datetime
        Date and time
    :param second: datetime
        Date and time to subtract to first
    :return: int
        Total difference in hours
    """

    return get_delta_seconds(first, second) / SECONDS_IN_HOUR


def dates_to_floats(lst):
    """
    :param lst: [] of datetime
        List of dates
    :return: [] of float
        List of floats (seconds since epoch)
    """

    return [
        datetime_to_unix_timestamp_s(date_time) for date_time in lst
    ]


def floats_to_dates(lst):
    """
    :param lst: [] of float
        List of floats (seconds since epoch)
    :return: [] of datetime
        List of dates
    """

    return [
        unix_timestamp_s_to_datetime(date_time) for date_time in lst
    ]


def parse_timedelta(raw):
    """
    :param raw: str
        Time interval written in short format
    :return: timedelta
        Time delta
    """

    tokens = ["s", "m", "h", "d", "w"]
    time_token = 0.0
    for tok in tokens:
        if raw.endswith(tok):
            time_token = float(raw.split(tok)[0])

    if raw.endswith("s"):
        return timedelta(seconds=time_token)
    elif raw.endswith("m"):
        return timedelta(minutes=time_token)
    elif raw.endswith("h"):
        return timedelta(hours=time_token)
    elif raw.endswith("d"):
        return timedelta(days=time_token)
    elif raw.endswith("w"):
        return timedelta(days=7 * time_token)
    else:
        raise ValueError("Cannot parse update interval", raw)
