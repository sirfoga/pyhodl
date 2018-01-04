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

import abc
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import spline  # todo fix deprecated

from pyhodl.config import VALUE_KEY
from pyhodl.core.models.exchanges import Portfolio
from pyhodl.utils.dates import generate_dates, dates_to_floats, floats_to_dates
from pyhodl.utils.misc import normalize


class CryptoPlotter:
    """ Plots crypto data """

    def __init__(self, wallets):
        self.wallets = wallets
        self.fig, self.axis = plt.subplots()

    @staticmethod
    def compute_trend(x, y, new_points, smooth_points):
        """
        :param x:[] of *
            X-axis data
        :param y: [] of float
            List of values
        :param new_points: int
            Number of points to generate
        :param smooth_points: int
            Number of points to interpolate
        :return: tuple ([] of *, [] of float)
            New dataset generated and smoothed values of new dataset
        """

        is_dates = isinstance(x[0], datetime)
        if is_dates:
            x = dates_to_floats(x)

        x = np.array(x)
        x_new = np.linspace(x.min(), x.max(), smooth_points)
        y_new = spline(x, y, x_new)

        if is_dates:
            x_new = floats_to_dates(x_new)

        return x_new, y_new

    def plot(self, x, y, label, with_trend=True):
        """
        :param x: [] of *
            X-axis data
        :param y: [] of float
            List of values
        :param label: str
            Label of data points
        :param with_trend: bool
            True iff you want to plot also trend
        :return: void
            Plot data
        """

        plt.plot(x, y, label=label)
        if with_trend:
            smooth_points = 30
            pred_points = 300
            x_new, y_new = self.compute_trend(x, y, 1, smooth_points)
            plt.plot(x_new, y_new, label="smooth")

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


class BalancePlotter(CryptoPlotter):
    """ Plots balance data of each coin for each date available """

    def __init__(self, wallets):
        CryptoPlotter.__init__(self, wallets)
        self.portfolio = Portfolio(self.wallets)

    def plot_balances(self):
        """
        :return: void
            Plots balances for each date for each coin
        """

        dates = self.portfolio.get_transactions_dates()
        for wallet in self.wallets:
            balances = wallet.get_balance_by_date(dates)
            plt.plot(
                dates,
                [b[VALUE_KEY] for b in balances],
                "-x",
                label="Amount of " + wallet.base_currency
            )

    def plot_delta_balances(self):
        """
        :return: void
            Plots balances for each date for each coin
        """

        for wallet in self.wallets:
            try:
                self._plot_delta_balance(wallet)
            except:
                print("Cannot plot delta balances wallet", wallet)

    @staticmethod
    def _plot_delta_balance(wallet):
        """
        :param wallet: Wallet
            Coin wallet with transactions
        :return: void
            Plots balances for transaction of coin
        """

        deltas = list(wallet.get_delta_by_transaction())
        dates = [
            balance["transaction"].date for balance in deltas
        ]
        subtotals = [
            float(balance[VALUE_KEY]) for balance in deltas
        ]

        plt.plot(
            dates,
            subtotals,
            "-o",
            label=wallet.base_currency + " delta"
        )

    def show(self, title, x_label="Time", y_label="Balances"):
        super().show(title, x_label, y_label)


class FiatPlotter(BalancePlotter):
    """ Plots coins-equivalent of your wallet """

    def __init__(self, wallets, base_currency="USD"):
        BalancePlotter.__init__(self, wallets)

        self.base_currency = base_currency
        self.wallets_value = {
            wallet.base_currency: wallet.balance(self.base_currency)
            for wallet in self.wallets
        }

    def plot_balances(self):
        """
        :return: void
            Plots balances for transaction of coin
        """

        dates = self.portfolio.get_transactions_dates()
        for wallet in self.wallets:
            balances = wallet.get_balance_by_date(dates, self.base_currency)
            label = "Value of " + wallet.base_currency + " (" + \
                    self.base_currency + ")"
            self.plot(dates, balances, label)

    def plot_buy_sells(self, wallet):
        """
        :param wallet: Wallet
            Coin wallet to plot
        :return: void
            Plots buy/sells points of coin against coin price
        """

        deltas = wallet.get_delta_by_transaction()
        dates = list(generate_dates(
            deltas[0]["transaction"].date,
            deltas[-1]["transaction"].date,
            hours=4
        ))
        price = wallet.get_price_on(dates, self.base_currency)
        plt.plot(
            dates, price,
            label=wallet.base_currency + " " + self.base_currency + "price"
        )  # plot price

        max_delta = max(abs(delta[VALUE_KEY]) for delta in deltas)
        for delta in deltas:  # plot buys/sells points
            val = delta[VALUE_KEY]
            if val < 0:
                color = "r"
            else:
                color = "g"

            # the bigger the radius the more you bought/sold
            radius = normalize(abs(val), 0, max_delta, 5, 15)
            date = delta["transaction"].date
            plt.plot(
                [date],
                [wallet.convert_to(date, self.base_currency)],
                marker="o",
                markersize=int(radius),
                color=color
            )

    def plot_crypto_fiat_balance(self):
        """
        :return: void
            Total balance for wach coin
        """

        dates, crypto_values, fiat_values = \
            self.portfolio.get_crypto_fiat_balance(self.base_currency)

        self.plot(
            dates, crypto_values,
            label="Crypto value of portfolio (" + self.base_currency + ")"
        )

        self.plot(
            dates, fiat_values,
            label="Fiat value of portfolio (" + self.base_currency + ")"
        )

    def show(self, title, x_label="Time", y_label="value"):
        super().show(title, x_label, self.base_currency + " " + y_label)
