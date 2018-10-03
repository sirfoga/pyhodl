# !/usr/bin/python3
# coding: utf_8


""" Updates local Gdax data """

from pyhodl.updater.models import ExchangeUpdater


class GdaxUpdater(ExchangeUpdater):
    """ Updates Gdax data """

    def __init__(self, api_client, data_folder):
        ExchangeUpdater.__init__(self, api_client, data_folder)

        self.accounts = self.client.get_accounts()
        self.accounts = {
            account["id"]: account for account in self.accounts
        }  # list -> dict
        self.transactions = {
            account_id: [] for account_id in self.accounts
        }

    def get_account_transactions(self, account):
        """
        :param account: {}
            Account to fetch
        :return: [] of {}
            List of transactions of account
        """

        transactions = []
        pages = self.client.get_account_history(account["id"])
        for page in pages:
            transactions += page

        if transactions:  # add currency symbol
            for i, _ in enumerate(transactions):
                transactions[i]["currency"] = account["currency"]
        return transactions

    def get_transactions(self):
        super().get_transactions()
        for account_id, account in self.accounts.items():
            self.log("Getting transaction history of account",
                     account["id"], "(" + account["currency"] + ")")
            self.transactions[account_id] = \
                self.get_account_transactions(account)
