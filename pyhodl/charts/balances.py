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

import matplotlib.pylab as plt

from ..data.core import BalancesParser


class Plotter(object):
    """ Plots data """

    def __init__(self, input_file, exchange_name, base_currency="USD"):
        """
        :param input_file: str
            File to parse
        :param exchange_name: str
            Name of exchange
        """

        self.data = sorted(
            BalancesParser(input_file).balances,
            key=lambda x: x["date"]
        )
        self.data = {
            self.data[i]["date"]: self.data[i]
            for i, date in enumerate(self.data)
        }
        self.dates = sorted(self.data.keys())
        self.coins = self.data[list(self.data.keys())[0]].keys()
        self.coins = [
            coin for coin in self.coins if coin != "date"
        ]
        self.exchange_name = str(exchange_name)
        self.currency = base_currency

        plt.grid(True)

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

    def plot_equiv(self, min_to_plot=0.01):
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

            if values[-1] > min_to_plot * total_cap:
                plt.plot(
                    self.dates,
                    values,
                    "-o",
                    label=coin
                )  # plot data

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
                if float(self.data[self.dates[-1]][coin]) > 0
            ])
            for date in self.dates
        ]

        plt.plot(
            self.dates,
            values,
            "--",
            label=self.currency + " equivalent"
        )  # plot data

    def plot(self):
        """
        :return: void
            Shows plot
        """

        plt.xlabel("Time")
        plt.ylabel("Amount")
        plt.title(self.exchange_name + " balance")
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
