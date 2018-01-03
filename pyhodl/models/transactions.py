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

import pytz

from pyhodl.data.coins import Coin


class TransactionType(Enum):
    """ Deposit, withdrawal ... """

    NULL = 0
    DEPOSIT = 1
    WITHDRAWAL = 2
    TRADING = 3
    FUNDING = 4
    ORDER = 5
    COMMISSION = 6


class CoinAmount:
    """ Amount of coin """

    def __init__(self, coin, amount):
        self.coin = Coin(coin) if coin else None
        self.amount = float(amount) if amount else None


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
        self.date = pytz.utc.localize(date) if not date.tzinfo else date
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

    def is_trade(self):
        """
        :return: bool
            True iff data is a trading
        """

        return self.transaction_type == TransactionType.TRADING

    def is_deposit(self):
        """
        :return: bool
            True iff data is a deposit
        """

        return self.transaction_type == TransactionType.DEPOSIT

    def is_fee(self):
        """
        :return: bool
            True iff data is a fee
        """

        return self.transaction_type == TransactionType.COMMISSION

    def is_withdrawal(self):
        """
        :return: bool
            True iff data is a withdrawal
        """

        return self.transaction_type == TransactionType.WITHDRAWAL

    def get_amount_buy_sell(self, coin):
        """
        :param coin: str
            Coin to get
        :return: float
            Amount of coin trade
        """

        amount = 0.0
        if self.is_trade():
            if self.coin_buy == coin:
                amount += self.buy_amount

            if self.coin_sell == coin:
                amount -= self.sell_amount
        return amount

    def get_amount_traded(self, coin):
        """
        :param coin: str
            Coin to get
        :return: float
            Amount of coin trade
        """

        amount = self.get_amount_buy_sell(coin)

        if self.is_trade():
            if self.commission and self.commission.coin == coin:
                amount -= self.commission.amount

        return amount

    def get_amount_commission(self, coin):
        """
        :param coin: str
            Coin to get
        :return: float
            Amount of coin fee
        """

        amount = 0.0
        if self.is_fee() and self.commission.coin == coin:
            amount -= self.commission.amount
        return amount

    def get_amount_moved(self, coin):
        """
        :param coin: str
            Coin to get
        :return: float
            Amount of coin moved (withdrawn/deposited)
        """

        amount = 0.0
        if self.is_deposit() and self.coin_buy == coin:
            amount += self.buy_amount

        if self.is_withdrawal() and self.coin_sell == coin:
            amount -= self.sell_amount
        return amount

    def get_amount(self, coin):
        """
        :param coin: str
            Coin to get
        :return: float
            Amount of coin in transaction
        """

        amount = self.get_amount_traded(coin)
        amount += self.get_amount_commission(coin)
        amount += self.get_amount_moved(coin)
        return amount

    def get_coins(self):
        """
        :return: tuple (str, str, str)
            Coin buy, coin sell and coin fee
        """

        coin_buy, coin_sell, coin_fee = self.coin_buy, self.coin_sell, None

        if self.commission:
            coin_fee = self.commission.coin

        coins = {coin_buy, coin_sell, coin_fee}  # set
        return {
            coin for coin in coins if coin and str(coin) != "None"
        }  # only valid coins

    def __getitem__(self, key):
        return self.raw[key]

    def __str__(self):
        out = "Transaction on " + str(self.date)
        out += self.amount_to_str(self.buy_amount, self.coin_buy, "+")
        out += self.amount_to_str(self.sell_amount, self.coin_sell, "-")
        if self.commission:
            out += "\nPaying " + str(self.commission.amount) + " " + \
                   str(self.commission.coin) + " as fee"

        out += "\nSuccessful? " + str(self.successful)

        return out

    @staticmethod
    def amount_to_str(amount, coin, prefix):
        if amount > 0:
            return "\n" + prefix + str(amount) + " " + str(coin)

        return ""


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

        self.coin = self.coin_sell
        self.amount = self.sell_amount
