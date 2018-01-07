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

from pyhodl.charts.core import CryptoPlotter
from pyhodl.config import VALUE_KEY
from pyhodl.core.models.exchanges import Portfolio
from pyhodl.utils.dates import generate_dates
from pyhodl.utils.misc import normalize


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

    def plot_price(self, wallet):
        """
        :param wallet: Wallet
            Coin wallet to plot
        :return: void
            Plots price of coin wallet
        """

        dates = wallet.dates()
        dates = list(generate_dates(dates[0], dates[-1], hours=4))
        price = wallet.get_price_on(dates, self.base_currency)
        self.plot(
            dates, price,
            wallet.base_currency + " " + self.base_currency + "price"
        )  # plot price

    def plot_delta_buy_sells(self, wallet):
        """
        :param wallet: Wallet
            Coin wallet to plot
        :return: void
            Plots buy/sells points of coin
        """

        deltas = wallet.get_delta_by_transaction()
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

    def plot_buy_sells(self, wallet):
        """
        :param wallet: Wallet
            Coin wallet to plot
        :return: void
            Plots buy/sells points of coin against coin price
        """

        if isinstance(wallet, str):  # specified the coin of the wallet
            wallet = self.get_wallet_by_coin(wallet)

        self.plot_price(wallet)
        self.plot_delta_buy_sells(wallet)

    def plot_account_value(self):
        """
        :return: void
            Total balance for coin
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

        self.plot_crypto_net()

    def plot_crypto_net(self):
        """
        :return: void
            Crypto net (bought - spent) of your portfolio
        """

        dates, crypto_net = \
            self.portfolio.get_crypto_net_balance(self.base_currency)

        self.plot(
            dates, crypto_net,
            label="Net value of portfolio (" + self.base_currency + ")"
        )

    def show(self, title, x_label="Time", y_label="value"):
        super().show(title, x_label, self.base_currency + " " + y_label)
