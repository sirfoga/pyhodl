# !/usr/bin/python3
# coding: utf_8


""" Analyze transactions in exchanges """

from .wallets import Wallet


class CryptoExchange:
    """ Exchange dealing with crypto-coins """

    def __init__(self, transactions, exchange_name):
        """
        :param transactions: [] of Transaction
            List of transactions
        """

        self.transactions = transactions
        if not self.transactions:
            raise ValueError("Creating exchange with no past transaction!")
        self.exchange_name = str(exchange_name)

    def get_transactions_count(self):
        """
        :return: int
            Number of transactions
        """

        return len(self.transactions)

    def get_first_transaction(self):
        """
        :return: Transaction
            First transaction done (with respect to time)
        """

        first = self.transactions[0]
        for transaction in self.transactions:
            if transaction.date < first.date:
                first = transaction
        return first

    def get_last_transaction(self):
        """
        :return: Transaction
            Last transaction done (with respect to time)
        """

        last = self.transactions[0]
        for transaction in self.transactions:
            if transaction.date > last.date:
                last = transaction
        return last

    def get_transactions(self, rule):
        """
        :param rule: func
            Evaluate this function on each transaction as a filter
        :return: generator of [] of Transaction
            List of transactions done between the dates
        """

        for transaction in self.transactions:
            if rule(transaction):
                yield transaction

    def build_wallets(self):
        """
        :return: {} of str -> Wallet
            Build a wallet for each currency traded and put trading history
            there
        """

        wallets = {}  # get only successful transactions
        transactions = self.get_transactions(lambda x: x.successful)
        for transaction in transactions:
            for coin in transaction.get_coins():
                if coin not in wallets:
                    wallets[coin] = Wallet(coin)

                wallets[coin].add_transaction(transaction)

        return wallets
