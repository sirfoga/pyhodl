#!/usr/bin/env python
# coding: utf-8

import random

from sklearn.preprocessing import minmax_scale

from btp.strategy import reward
from btp.strategy import should_buy, should_sell


def extract_data(data, n, m, n_train_samples):
    Xs = []
    ys = []

    for _ in range(n_train_samples):
        # todo improve sampling
        i = random.randint(n, len(data) - 1 - m)

        # input
        X = data['Open'][i - n: i]
        Xs.append(minmax_scale(X))  # scale

        # output
        y = 0  # do nothing

        current_price = data['Open'][i]
        past_m = int(m / 2)
        future = data['Open'][i: i + m].tolist()
        time_frame = data['Open'][i - past_m: i + m].tolist()

        local_min = min(time_frame)
        local_max = max(time_frame)
        next_max = max(future)
        next_min = min(future)
        a = 0.2 / 100  # 0.5 % quantiles

        if current_price <= local_min * (1 + a):
            if should_buy(current_price, next_max):
                y = reward(current_price, next_max)

                # todo debug print('BUY {} -> {} ({})'.format(current_price, next_max, y))

        if current_price >= local_max * (1 - a):
            if should_sell(current_price, next_min):
                y = reward(current_price, next_min)  # sell

                # todo debug print('SELL {} -> {} ({})'.format(current_price, next_min, y))

        ys.append(y)

    return Xs, ys


def train_model(data, n, m, n_samples, trainer):
    """ predict price afer N moves from last M prices using a regression model """

    X, y = extract_data(data, n, m, n_samples)
    model = trainer(X, y)
    return model


def score_model(data, n, m, n_samples, model):
    X, y = extract_data(data, n, m, n_samples)
    return model.score(X, y)
