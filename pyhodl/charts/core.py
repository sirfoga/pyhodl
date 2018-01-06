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


""" Plot data with trends and stats """

import abc
from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import spline
from sklearn import neighbors

from pyhodl.utils.dates import dates_to_floats, floats_to_dates
from pyhodl.utils.misc import remove_same_coordinates


class CryptoPlotter:
    """ Plots crypto data """

    def __init__(self, wallets):
        self.wallets = wallets
        self.fig, self.axis = plt.subplots()

    @staticmethod
    def compute_knn_trend(x_data, y_val, smooth_points):
        """
        :param x_data:[] of *
            X-axis data
        :param y_val: [] of float
            List of values
        :param smooth_points: int
            Number of points to interpolate
        :return: tuple ([] of *, [] of float)
            New dataset generated (with knn) values of new dataset
        """

        is_dates = isinstance(x_data[0], datetime)
        if is_dates:
            x_data = dates_to_floats(x_data)

        n_neighbors = 11
        weights = "uniform"
        knn = neighbors.KNeighborsRegressor(n_neighbors, weights=weights)

        x_data = np.array(x_data).reshape(-1, 1)
        new_x = np.linspace(x_data.min(), x_data.max(), smooth_points)
        new_x = np.array([new_x]).reshape(-1, 1)
        y_prediction = knn.fit(x_data, y_val).predict(new_x)

        if is_dates:
            new_x = floats_to_dates(new_x[:, 0])

        return new_x, y_prediction

    @staticmethod
    def compute_trend(x_data, y_val, smooth_points):
        """
        :param x_data:[] of *
            X-axis data
        :param y_val: [] of float
            List of values
        :param smooth_points: int
            Number of points to interpolate
        :return: tuple ([] of *, [] of float)
            New dataset generated and smoothed values of new dataset
        """

        is_dates = isinstance(x_data[0], datetime)
        if is_dates:
            x_data = dates_to_floats(x_data)

        x_data, y_val = remove_same_coordinates(x_data, y_val)
        x_new = np.linspace(x_data.min(), x_data.max(), smooth_points)
        y_new = spline(x_data, y_val, x_new)

        if is_dates:
            x_new = floats_to_dates(x_new[:, 0])

        return x_new, y_new

    @staticmethod
    def plot(x_data, y_val, label, with_trend=False):
        """
        :param x_data: [] of *
            X-axis data
        :param y_val: [] of float
            List of values
        :param label: str
            Label of data points
        :param with_trend: bool
            True iff you want to plot also trend
        :return: void
            Plot data
        """

        plt.plot(x_data, y_val, "-", label=label)
        if with_trend:
            smooth_points = 300
            x_new, y_new = CryptoPlotter.compute_trend(x_data, y_val,
                                                       smooth_points)
            plt.plot(x_new, y_new, label=label + " trend")

    @abc.abstractmethod
    def show(self, title, x_label="Time", y_label="Amount"):
        """
        :param y_label: str
            Label of Y-axis
        :param x_label: str
            Label of X-axis
        :param title: str
            Title of plot
        :return: void
            Shows plot
        """

        plt.grid(True)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.legend()  # build legend
        plt.show()

    def get_wallet_by_coin(self, coin):
        """
        :param coin: str
            Coin
        :return: Wallet
            Wallet with base coin specified
        """

        coin = coin.upper()
        candidate = [
            wallet for wallet in self.wallets if wallet.base_currency == coin
        ]
        if candidate:
            return candidate[0]

        raise ValueError("Cannot find wallet with coin", coin)
