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
