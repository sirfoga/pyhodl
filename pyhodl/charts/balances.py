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

import matplotlib.pyplot as plt

from pyhodl.app import VALUE_KEY, DATE_TIME_KEY
from pyhodl.stats.transactions import get_total_equivalent_balances
from pyhodl.utils import generate_dates, normalize


class CryptoPlotter:
    """ Plots crypto data """

    def __init__(self):
        self.fig, self.ax = plt.subplots()

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
        CryptoPlotter.__init__(self)
        self.wallets = wallets

    def plot_balances(self):
        """
        :return: void
            Plots balances for each date for each coin
        :return min_perc: float in [0, 1]
            Hide small asset that are below this percentage of the wallet value
        """

        for wallet in self.wallets:
            try:
                self._plot_balance(wallet)
            except Exception as e:
                print("Cannot plot balances of wallet",
                      wallet, "due to", e)

    def plot_delta_balances(self):
        """
        :return: void
            Plots balances for each date for each coin
        """

        for wallet in self.wallets:
            try:
                self._plot_delta_balance(wallet)
            except Exception as e:
                print("Cannot plot delta balances wallet",
                      wallet, "due to", e)

    def _plot_balance(self, wallet):
        """
        :param wallet: Wallet
            Coin wallet with transactions
        :return: void
            Plots balances for transaction of coin
        """

        balances = list(wallet.get_balances_by_transaction())
        dates = [
            balance["transaction"].date for balance in balances
        ]
        subtotals = [
            float(balance[VALUE_KEY]) for balance in balances
        ]

        plt.plot(
            dates,
            subtotals,
            "-x",
            label=wallet.base_currency
        )

    def _plot_delta_balance(self, wallet):
        """
        :param wallet: Wallet
            Coin wallet with transactions
        :return: void
            Plots balances for transaction of coin
        """

        deltas = list(wallet.get_delta_balance_by_transaction())
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


class OtherCurrencyPlotter(BalancePlotter):
    """ Plots coins-equivalent of your wallet """

    def __init__(self, wallets, base_currency="USD"):
        BalancePlotter.__init__(self, wallets)

        self.base_currency = base_currency
        self.wallets_value = {
            wallet.base_currency:
                wallet.get_balance_equivalent(self.base_currency)
            for wallet in self.wallets
        }

    def _plot_balance(self, wallet):
        """
        :param wallet: Wallet
            Coin wallet with transactions
        :return: void
            Plots balances for transaction of coin
        """

        balances = list(wallet.get_balances_by_transaction())
        dates = [
            balance["transaction"].date for balance in balances
        ]
        subtotals = [
            wallet.get_equivalent(
                balance["transaction"].date,
                self.base_currency,
                float(balance[VALUE_KEY])
            ) for balance in balances
        ]

        plt.plot(
            dates,
            subtotals,
            "-x",
            label=wallet.base_currency + " - " + self.base_currency + " value"
        )

    def plot_buy_sells(self, wallet):
        """
        :param wallet: Wallet
            Coin wallet to plot
        :return: void
            Plots buy/sells points of coin against coin price
        """

        deltas = list(wallet.get_delta_balance_by_transaction())
        dates = list(generate_dates(
            deltas[0]["transaction"].date,
            deltas[-1]["transaction"].date,
            hours=4
        ))
        equivalents = [
            wallet.get_equivalent(date, self.base_currency) for date in dates
        ]
        plt.plot(
            dates,
            equivalents,
            label=wallet.base_currency + " " + self.base_currency + " price"
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
                [wallet.get_equivalent(date, self.base_currency)],
                marker="o",
                markersize=int(radius),
                color=color
            )

    def plot_total_balances(self):
        balances = get_total_equivalent_balances(
            self.wallets, self.base_currency
        )
        plt.plot(
            [balance[DATE_TIME_KEY] for balance in balances],
            [balance[VALUE_KEY] for balance in balances],
            label="Total " + self.base_currency + " value of wallets"
        )  # plot price

    def show(self, title, x_label="Time", y_label="value"):
        super().show(title, x_label, self.base_currency + " " + y_label)
