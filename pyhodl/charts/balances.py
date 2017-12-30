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

    def __init__(self, exchange):
        """
        :param exchange: CryptoExchange
            Exchange with transactions
        """

        CryptoPlotter.__init__(self)

        self.exchange = exchange
        self.wallets = self.exchange.build_wallets()  # dict <str: Wallet>

    def plot_balances(self):
        """
        :return: void
            Plots balances for each date for each coin
        """

        for coin, wallet in self.wallets.items():
            try:
                self.plot_balance(wallet)
            except Exception as e:
                print("Cannot plot balances of", coin, "with wallet",
                      wallet, "due to", e)

    def plot_balance(self, wallet):
        """
        :param wallet: Wallet
            Coin wallet with transactions
        :return: void
            Plots balances for transaction of coin
        """

        balances = wallet.get_balances_by_transaction()
        dates = [
            balance["transaction"].date for balance in balances
        ]
        subtotals = [
            float(balance["balance"]) for balance in balances
        ]

        plt.plot(
            dates,
            subtotals,
            "-x",
            label=wallet.currency
        )


class FiatPlotter(CryptoPlotter):
    """ Plots fiat equivalent of your wallet """
