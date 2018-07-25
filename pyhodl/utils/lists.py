# !/usr/bin/python3
# coding: utf_8


""" Deal with lists and other containers """

from collections import Counter


def get_full_lists(big_dict):
    """
    :param big_dict: {}
        Dict of similar dicts with varying keys
    :return: {} of {}
        Big dict of dicts with same keys (the dates).
    """

    big_counter = Counter()
    for _, inner_dict in big_dict.items():
        big_counter += inner_dict
    all_keys = big_counter.keys()
    return {
        key: {
            inner_key: inner_value[key] if key in inner_value else None
            for inner_key, inner_value in big_dict.items()
        } for key in all_keys
    }


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


def middle(lst):
    """
    :param lst: [] of *
        List
    :return: *
        Object in the middle. In case of ambiguity, take the first one
    """

    middle_point = len(lst) / 2
    return lst[middle_point]


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
