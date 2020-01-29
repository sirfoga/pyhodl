#!/usr/bin/env python
# coding: utf-8

from btp.finance import get_profit


def should_buy(current_price, next_price):
    if current_price < next_price:
        return get_profit(current_price, next_price) > 0
    return False


def should_sell(current_price, next_price):
    if current_price > next_price:
        return get_profit(current_price, next_price) > 0
    return False


def reward(current_price, next_price):
    # todo return get_profit(current_price, next_price) / current_price

    if current_price < next_price:
        return +1  # buy

    if current_price > next_price:
        return -1  # sell

    return 0
