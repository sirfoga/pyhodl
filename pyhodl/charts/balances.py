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

    def __init__(self, input_file, exchange_name):
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

    def plot_amount(self):
        """
        :return: void
            Plots coins amount
        """

        coins = [
            coin for coin in self.coins
            if "value" not in coin
        ]

        plt.grid(True)
        for coin in coins:
            values = [
                self.data[date][coin] for date in self.dates
            ]

            plt.plot(
                self.dates,
                values,
                label=coin
            )  # plot data

        plt.xlabel("Time")
        plt.ylabel("Amount")
        plt.legend()  # build legend
        plt.title(self.exchange_name + " amount of each coin")
        plt.show()

    def plot_equiv(self):
        """
        :return:
        """

        pass

    def plot_total_equiv(self):
        """
        :return:
        """

        pass

    def plot(self):
        """
        :return:
        """

        pass

    def plot_coin(self, coin):
        """
        :param coin:
        :return:
        """

        pass
