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


""" Plot balances data with trends and stats """

import time

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from ..data.core import BalanceParser


def func(x, a1, b1, a2, b2, a3, c):
    return a1 * np.sin(b1 * x) + a2 * np.cos(b2 * x) + a3 * np.power(x, 4) + c


class Plotter(object):
    """ Plots data """

    def __init__(self, input_file, base_currency="USD"):
        """
        :param input_file: str
            File to parse
        """

        object.__init__(self)

        self.parser = BalanceParser(input_file)
        self.data = sorted(self.parser.balances, key=lambda x: x["date"])
        self.data = {
            self.data[i]["date"]: self.data[i]
            for i, date in enumerate(self.data)
        }
        self.dates = sorted(self.data.keys())
        self.x_dates = mdates.date2num(self.dates)
        self.unix_timestamps = [
            int(time.mktime(date.timetuple())) for date in self.dates
        ]
        self.coins = self.data[list(self.data.keys())[0]].keys()
        self.coins = [
            coin for coin in self.coins if coin != "date"
        ]
        self.currency = base_currency
        self.trend_deg = 8
        self.trend_dates = np.linspace(
            self.x_dates.min(), self.x_dates.max(), 200
        )

    def plot_amount(self):
        """
        :return: void
            Adds to chart coins amount
        """

        coins = [
            coin for coin in self.coins
            if "value" not in coin
        ]

        for coin in coins:
            values = [
                self.data[date][coin] for date in self.dates
            ]

            plt.plot(
                self.dates,
                values,
                "-o",
                label=coin
            )  # plot data

    def plot_equiv(self, min_to_plot=0.33):
        """
        :param min_to_plot: float
            Min percentage of total cap to plot coin equivalent
        :return: void
            Plots currency equivalent for each coin
        """

        coins = [
            coin for coin in self.coins
            if "value" in coin
        ]
        total_cap = self.get_last_total()

        for coin in coins:
            values = [
                self.data[date][coin] for date in self.dates
            ]

            if max(values) > min_to_plot * total_cap:
                popt, pcov = curve_fit(func, self.x_dates, values)
                plt.plot(
                    mdates.num2date(self.x_dates),
                    func(self.x_dates, *popt), "-", label=coin
                )  # trend

    def plot_total_equiv(self):
        """
        :return: void
            Adds to chart total equiv
        """

        coins = [
            coin for coin in self.coins
            if "value" in coin
        ]

        values = [
            sum([
                self.data[date][coin] for coin in coins
                if float(self.data[date][coin]) > 0
            ])
            for date in self.dates
        ]

        popt, pcov = curve_fit(func, self.x_dates, values)
        plt.plot(
            mdates.num2date(self.x_dates), func(self.x_dates, *popt), "--",
            label=self.currency + " equivalent"
        )  # trend

    def plot(self):
        """
        :return: void
            Shows plot
        """

        plt.grid(True)
        plt.xlabel("Time")
        plt.ylabel("Amount")
        plt.title("Data taken from " + self.parser.filename)
        plt.legend()  # build legend
        plt.show()

    def get_last_total(self):
        """
        :return: float
            Total equivalent (last indexed)
        """

        coins = [
            coin for coin in self.coins
            if "value" in coin
        ]

        return sum([
            self.data[self.dates[-1]][coin] for coin in coins
            if float(self.data[self.dates[-1]][coin]) > 0
        ])
