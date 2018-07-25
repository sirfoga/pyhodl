# !/usr/bin/python3
# coding: utf_8


""" Updates local Binance data """

from pyhodl.updater.models import ExchangeUpdater
from pyhodl.utils.network import handle_rate_limits, get_and_sleep


class BinanceUpdater(ExchangeUpdater):
    """ Updates Binance data """

    def get_symbols_list(self):
        """
        :return: [] of str
            List of symbols (currencies)
        """

        symbols = self.client.get_all_tickers()
        return [
            symbol["symbol"] for symbol in symbols
        ]

    @handle_rate_limits
    def get_deposits(self):
        """
        :return: [] of {}
            List of exchange deposits
        """

        return self.client.get_deposit_history()["depositList"]

    @handle_rate_limits
    def get_withdraw(self):
        """
        :return: [] of {}
            List of exchange withdrawals
        """

        return self.client.get_withdraw_history()["withdrawList"]

    @handle_rate_limits
    def get_all_transactions(self, symbol, from_id=0, page_size=500):
        """
        :return: [] of {}
            List of exchange transactions
        """

        trades = self.client.get_my_trades(symbol=symbol, fromId=from_id)
        for i, _ in enumerate(trades):
            trades[i]["symbol"] = symbol

        if trades:  # if page returns some trades, search for others
            last_id = trades[-1]["id"]
            next_id = last_id + page_size + 1
            new_trades = self.get_all_transactions(
                symbol=symbol, from_id=next_id
            )
            if new_trades:
                trades += new_trades

        return trades

    def get_transactions(self):
        """
        :return: [] of {}
            List of all exchange movements (transactions + deposits +
            withdrawals)
        """

        super().get_transactions()
        transactions = get_and_sleep(
            self.get_symbols_list(),
            self.get_all_transactions,
            self.rate,
            "transactions"
        )
        self.transactions = \
            transactions + self.get_deposits() + self.get_withdraw()
