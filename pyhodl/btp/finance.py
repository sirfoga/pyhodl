#!/usr/bin/env python
# coding: utf-8

from btp.maths import find_local_min_max

FEES = (0, 0.01)


def get_fee(price):
    """
    :param price: price of buy/sell
    :return: fee to buy/sell at that price
    """

    return FEES[0] + FEES[1] * price


def get_profit(current_price, next_price):
    """
    :param current_price: price now
    :param next_price: price later
    :return: profit of buying/selling now and selling/buying later
    """

    fee_sell = get_fee(current_price)  # no matter at what price you sell/buy
    fee_buy = get_fee(next_price)
    return abs(current_price - next_price) - fee_sell - fee_buy


def max_profit(prices, n_trades):
    """
    :param prices: price of stock
    :param n_trades: max number of trades
    :return: DP approach to get maximum profits doing at most trades
    """

    n = len(prices)

    # profit[t][i] stores maximum profit using atmost t transactions up to
    # time i (including day i)
    profit = [
        [0 for i in range(n + 1)]
        for j in range(n_trades + 1)
    ]

    for i in range(1, n_trades + 1):
        prev_diff = float('-inf')
        for j in range(1, n):
            prev_diff = max(
                prev_diff,
                profit[i - 1][j - 1] - prices[j - 1] - get_fee(prices[j - 1])
            )
            m_profit = max(
                profit[i][j - 1],  # do nothing
                prices[j] + prev_diff  # buy-sell
            )
            real_profit = m_profit - get_fee(prices[j])  # fee
            profit[i][j] = real_profit

    return profit[n_trades][n - 1]


def optimal_blsh_strategy(prices, n_trades):
    """
    :param prices: price of stock
    :param n_trades: max number of trades
    :return: profit following 'Buy Low Sell High' strategy knowing everything
    """

    min_maxs = find_local_min_max(prices)  # find local min/max
    prices = [local[1] for local in min_maxs]
    profit = max_profit(prices, n_trades)
    return profit
