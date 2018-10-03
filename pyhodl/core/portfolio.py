# !/usr/bin/python3
# coding: utf_8


""" Analyze transactions in wallets """

import numpy as np

from pyhodl.config import VALUE_KEY, NAN, DATE_TIME_KEY
from pyhodl.data.coins import DEFAULT_FIAT
from pyhodl.utils.misc import get_ratio, get_percentage, is_nan, \
    get_relative_delta, get_relative_percentage


class Portfolio:
    """ Contains wallets, of also different coins """

    def __init__(self, wallets, portfolio_name=None):
        self.wallets = wallets
        self.portfolio_name = str(portfolio_name) if portfolio_name else None

    def get_transactions_dates(self):
        """
        :return: [] of datetime
            List of all dates of all transactions of all wallets
        """

        dates = []
        for wallet in self.wallets:
            dates += wallet.dates()
        return sorted(dates)

    def get_current_balance(self, currency=DEFAULT_FIAT):
        """
        :return: [] of {}
            List of current balance by wallet
        """

        balances = [
            {
                "symbol": wallet.base_currency,
                "balance": wallet.balance(),
                VALUE_KEY: wallet.balance(currency, True)
            }
            for wallet in self.wallets
        ]
        tot_balance = self.sum_total_balance(balances)

        for i, balance in enumerate(balances):  # add price and %
            balances[i]["price"] = get_ratio(
                balance[VALUE_KEY],
                balance["balance"]
            )
            balances[i]["percentage"] = get_percentage(
                balance[VALUE_KEY],
                tot_balance
            )

        balances = sorted([
            balance for balance in balances if float(balance["balance"]) > 0.0
        ], key=lambda x: x[VALUE_KEY], reverse=True)

        return balances

    @staticmethod
    def get_balances_from_deltas(deltas):
        """
        :param deltas: [] of {}
            List of delta by transaction date
        :return: [] of {}
            List of subtotal balances by transaction date
        """

        if not deltas:
            return []

        deltas = sorted([
            delta for delta in deltas if delta[VALUE_KEY] != NAN
        ], key=lambda x: x[DATE_TIME_KEY])
        balances = [deltas[0]]
        for delta in deltas[1:]:
            balances.append({
                DATE_TIME_KEY: delta[DATE_TIME_KEY],
                VALUE_KEY: balances[-1][VALUE_KEY] + delta[VALUE_KEY]
            })
        return balances

    @staticmethod
    def sum_total_balance(balances):
        """
        :param balances: [] of {}
            List of raw balances
        :return: float
            Total balance (without counting NaN values)
        """

        if isinstance(balances, dict):
            return Portfolio.sum_total_balance(balances.values())

        return sum([
            balance[VALUE_KEY] for balance in balances
            if isinstance(balance, dict) and not is_nan(balance[VALUE_KEY])
        ])

    def get_crypto_fiat_balance(self, currency):
        """
        :return: tuple ([] of datetime, [] of float, [] of float)
            List of dates, balances of crypto coins and fiat balances
        """

        dates = self.get_transactions_dates()
        crypto_values = np.zeros(len(dates))  # zeros
        fiat_values = np.zeros(len(dates))

        for wallet in self.wallets:
            balances = wallet.get_balance_array_by_date(dates, currency)
            if wallet.is_crypto():
                crypto_values += balances
            else:
                fiat_values += balances
        return dates, crypto_values, fiat_values

    def get_crypto_net_balance(self, currency):
        """
        :return: tuple ([] of datetime, [] of float)
            List of dates, balances of crypto coins - fiat balances
        """

        dates, crypto_values, fiat_values = \
            self.get_crypto_fiat_balance(currency)

        crypto_net = crypto_values + fiat_values
        return dates, crypto_net

    def get_balance_info(self, last=None):
        """
        :param last: str
            Path to file where to read balance data
        :return: tuple
            current balance, total value, last total value, delta, delta %
        """

        balances = self.get_current_balance()
        total_value = self.sum_total_balance(balances)
        delta, delta_percentage, last_total = None, None, None

        if last:
            last_total_balance = sum([
                float(coin[VALUE_KEY])
                for symbol, coin in last.items() if symbol != DATE_TIME_KEY
            ])
            delta = get_relative_delta(total_value, last_total_balance)
            delta_percentage = get_relative_percentage(
                total_value,
                last_total_balance
            )
            last_total = self.sum_total_balance(last)

        return balances, total_value, last_total, delta, delta_percentage
