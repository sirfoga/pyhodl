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

from pyhodl.app import VALUE_KEY


class CryptoPlotter:
    """ Plots crypto data """

    def show(self, title):
        """
        :param title: str
            Title of plot
        :return: void
            Shows plot
        """

        plt.grid(True)
        plt.xlabel("Time")
        plt.ylabel("Amount")
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
            label=wallet.base_currency + "delta since last transaction"
        )


class OtherCurrencyPlotter(BalancePlotter):
    """ Plots fiat equivalent of your wallet """

    def __init__(self, wallets, base_currency="USD"):
        BalancePlotter.__init__(self, wallets)

        self.base_currency = base_currency
        self.wallets_value = {
            wallet.base_currency:
                wallet.get_balance_equivalent(self.base_currency)
            for wallet in self.wallets
        }

    def plot_balances(self, min_value=0.01):
        """
        :return: void
            Plots balances for each date for each coin
        :return min_value: float in [0, 1]
            Hide small asset that are below this percentage of the wallet value
        """

        min_to_plot = min_value * sum(self.wallets_value.values())
        for wallet in self.wallets:
            try:
                wallet_balance = self.wallets_value[wallet.base_currency]
                if wallet_balance > min_to_plot:
                    self._plot_balance(wallet)
            except Exception as e:
                print("Cannot plot balances equivalent of wallet",
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
            wallet.get_equivalent(
                balance["transaction"].date,
                self.base_currency,
                float(balance[VALUE_KEY])
            ) for balance in balances
        ]
        amounts = [
            float(balance[VALUE_KEY]) for balance in balances
        ]

        plt.plot(
            dates,
            subtotals,
            "-x",
            label=wallet.base_currency + " - " + self.base_currency + " value"
        )
