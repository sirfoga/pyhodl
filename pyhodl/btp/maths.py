#!/usr/bin/env python
# coding: utf-8


def diffs(items, order=1):
    """
    :param items: list
    :param order: oder of differences
    :return: diff between items
    """

    ds = items

    while order > 0:
        ds = [
            ds[i] - ds[i - 1]
            for i in range(1, len(ds))
        ]
        order -= 1

    return ds


def find_local_min_max(items):
    """
    :param items: list
    :return: [] of (index, value) with local min/max
    """

    ds = diffs(items)
    ls = [(0, items[0])]  # index, value
    prev_diff = 0
    for i, diff in enumerate(ds):
        if diff * prev_diff < 0:  # change of sign -> local min or max
            ls.append((i, items[i]))

        prev_diff = diff
    ls.append((len(items) - 1, items[-1]))
    return ls
