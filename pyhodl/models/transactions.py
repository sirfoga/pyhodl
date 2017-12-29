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


""" Core models """

from enum import Enum


class TransactionType(Enum):
    """ Deposit, withdrawal ... """

    NULL = 0
    DEPOSIT = 1
    WITHDRAWAL = 2
    TRADING = 3
    FUNDING = 4
    ORDER = 5
    COMMISSION = 6


class Transaction:
    """ Exchange transaction """

    def __init__(self, raw_dict,
                 coin_bought, buy_amount,
                 coin_sold, sell_amount, date,
                 trans_type=TransactionType.TRADING,
                 successful=True, commission=None):
        """
        :param raw_dict: {}
            Dict containing raw data
        :param trans_type: TransactionType
            Type of transactions
        :param date: date
            Date info
        :param successful: bool
            True iff transaction has actually taken place
        :param commission: Transaction
            Commission of transaction (if any)
        """

        self.raw = raw_dict
        self.coin_buy = str(coin_bought)
        self.buy_amount = float(buy_amount) if buy_amount else 0
        self.coin_sell = str(coin_sold)
        self.sell_amount = float(sell_amount) if sell_amount else 0
        self.transaction_type = trans_type
        self.date = date
        self.successful = bool(successful)
        self.commission = commission

    def get_attrs(self):
        """
        :return: []
            Keys of internal dict
        """

        return list(self.raw.keys())

    def has(self, item):
        """
        :param item: str
            Item to look for
        :return: bool
            True iff item is in any of the data
        """

        for key, value in self.raw.items():
            try:
                if str(item) in str(value) or str(item) in str(key):
                    return True
            except:
                pass
        return False

    def __getitem__(self, key):
        return self.raw[key]

    def __str__(self):
        return str(self.raw)


class Commission(Transaction):
    """ Transaction commission """

    def __init__(self, raw_dict, coin, amount, date, successful=True):
        """
        :param raw_dict: {}
            Dict containing raw data
        :param date: date
            Date info
        :param successful: bool
            True iff transaction has actually taken place
        """

        Transaction.__init__(
            self,
            raw_dict,
            coin_bought=None,
            buy_amount=None,
            coin_sold=coin,
            sell_amount=amount,
            date=date,
            trans_type=TransactionType.COMMISSION,
            successful=successful
        )


class Wallet:
    """ A general wallet, tracking addition, deletions and fees """

    def __init__(self, create_date, start_amount=0):
        """
        :param create_date: datetime
            Date of transaction
        ::param start_amount: float
            Amount of currency at start
        """

        self.balance = float(0)
        self.transactions = []  # list of operations performed

        if start_amount > 0:
            self.add(start_amount, create_date)
        elif start_amount < 0:
            self.remove(start_amount, create_date)

    def add(self, amount, date):
        """
        :param amount: float
            Amount to be added to balance
        :param date: datetime
            Date of transaction
        :return: void
            Adds amount to balance
        """

        self.transactions.append(
            Transaction(
                {
                    "action": "add",
                    "amount": abs(amount),
                    "date": date
                },
                date_key="date"
            )
        )

        self.balance += abs(amount)

    def remove(self, amount, date):
        """
        :param amount: float
            Amount to be removed to balance
        :param date: datetime
            Date of transaction
        :return: void
            Removes amount from balance
        """

        self.transactions.append(
            Transaction(
                {
                    "action": "remove",
                    "amount": -abs(amount),
                    "date": date
                },
                date_key="date"
            )
        )

        self.balance -= abs(amount)

    def get_balance(self):
        """
        :return: float
            Current balance
        """

        return self.balance

    def merge(self, other):
        """
        :param other: Wallet
            Other wallet to merge with
        :return: void
            Add other's transactions to this wallet
        """

        for transaction in other.transactions:  # redo same actions
            if transaction["action"] == "add":
                self.add(transaction["amount"], transaction.date)
            else:
                self.remove(transaction["amount"], transaction.date)

    def get_transactions_dict(self):
        """
        :return: [] of {}
            List of raw transactions
        """

        for transaction in self.transactions:
            yield {
                "date": transaction.date,
                "amount": transaction["amount"],
                "successful": True
            }

    def dates(self):
        """
        :return: [] of datetime
            List of all dates
        """

        return [
            transaction.date for transaction in self.transactions
        ]

    def get_amount(self, date):
        """
        :param date: datetime
            Date of transaction
        :return: float
            Amount exchanged with transaction in specified date
        """

        amount = float(0.0)

        for transaction in self.transactions:
            if transaction.date == date:
                amount += float(transaction["amount"])

        return amount


class Balance:
    """ Balance of something, expressed in many coins """

    def __init__(self, wallets):
        """
        :param wallets: {} of Wallet
            List of wallet (and coins)
        """

        self.wallets = wallets
        nan_keys = [
            key for key in wallets if str(key) == "nan"
        ]
        for key in nan_keys:
            del self.wallets[key]

    def merge(self, other):
        """
        :param other: Balance
            Other balance to merge with
        :return: void
            Merges other's wallets
        """

        for coin, wallet in other.wallets.items():
            if coin not in self.wallets:  # new coin
                self.wallets[coin] = wallet
            else:  # coin wallet has to be merged
                self.wallets[coin].merge(wallet)

    def get_balance(self):
        """
        :return: {} str -> float
            For each coin, evaluate balance
        """

        return {
            coin: wallet.get_balance() for coin, wallet in self.wallets.items()
        }
