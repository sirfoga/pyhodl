# !/usr/bin/python3
# coding: utf_8


""" Updates local Coinbase data """

from pyhodl.updater.models import ExchangeUpdater


class CoinbaseUpdater(ExchangeUpdater):
    """ Updates Coinbase data """

    def __init__(self, api_client, data_folder):
        ExchangeUpdater.__init__(self, api_client, data_folder)
        self.accounts = self.client.get_accounts()["data"]
        self.accounts = {
            account["id"]: account for account in self.accounts
        }  # list -> dict
        self.transactions = {
            account_id: [] for account_id in self.accounts
        }
        self.page_limit = 100  # reduced page limit for coinbase and gdax

    def get_account_transactions(self, account_id):
        """
        :param account_id: str
            Account to fetch
        :return: [] of {}
            List of transactions of account
        """

        raw_data = self.client.get_transactions(
            account_id,
            limit=self.page_limit
        )
        self.transactions[account_id] += raw_data["data"]

        while "pagination" in raw_data:  # other transactions
            raw_data = self.client.get_transaction(
                raw_data["pagination"]["previous_uri"]
            )
            self.transactions[account_id] += raw_data["data"]

    def get_transactions(self):
        super().get_transactions()
        for account_id, account in self.accounts.items():
            self.log("Getting transaction history of account",
                     account["id"], "(" + account["balance"]["currency"] + ")")
            self.get_account_transactions(account_id)
