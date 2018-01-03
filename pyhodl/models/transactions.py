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

from pyhodl.config import FIAT_COINS
from pyhodl.data.coins import Coin, CryptoCoin


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

    def __init__(self, coin, amount, is_in):
        self.coin = Coin(coin) if coin else None
        self.amount = float(amount) if amount else None
        self.is_in = bool(is_in) if is_in else False

    def get_symbol(self):
        if self.coin:
            if self.coin in FIAT_COINS:
                return self.coin
            return CryptoCoin(self.coin.symbol)
        return False

    def get_amount(self):
        return self.amount

    def __str__(self):
        prefix = "+" if self.is_in else "-"
        if self.amount > 0:
            return "\n" + prefix + str(self.amount) + " " + str(self.coin)

        return ""


class Transaction:
    """ Exchange transaction """

    def __init__(self, raw_dict, coin_in, coin_out, date,
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
        self.coin_buy = coin_in
        self.coin_sell = coin_out
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
        :param coin: Coin
            Coin to get
        :return: float
            Amount of coin trade
        """

        amount = 0.0
        if self.is_trade():
            if self.coin_buy and self.coin_buy.get_symbol() == coin:
                amount += self.coin_buy.get_amount()

            if self.coin_sell and self.coin_sell.get_symbol() == coin:
                amount -= self.coin_sell.get_amount()
        return amount

    def get_amount_traded(self, coin):
        """
        :param coin: Coin
            Coin to get
        :return: float
            Amount of coin trade
        """

        amount = self.get_amount_buy_sell(coin)
        if self.is_trade():
            if self.commission and self.commission.coin.get_symbol() == coin:
                amount -= self.commission.coin.get_amount()
        return amount

    def get_amount_commission(self, coin):
        """
        :param coin: Coin
            Coin to get
        :return: float
            Amount of coin fee
        """

        amount = 0.0
        if self.is_fee() and self.commission and \
                        self.commission.coin.get_symbol() == coin:
            amount -= self.commission.coin.get_amount()
        return amount

    def get_amount_moved(self, coin):
        """
        :param coin: Coin
            Coin to get
        :return: float
            Amount of coin moved (withdrawn/deposited)
        """

        amount = 0.0
        if self.is_deposit() and self.coin_buy and \
                        self.coin_buy.get_symbol() == coin:
            amount += self.coin_buy.get_amount()

        if self.is_withdrawal() and self.coin_sell and \
                        self.coin_sell.get_symbol() == coin:
            amount -= self.coin_sell.get_amount()
        return amount

    def get_amount(self, coin):
        """
        :param coin: Coin
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

        coins = [coin_buy, coin_sell, coin_fee]
        coins = [coin.get_symbol() for coin in coins if coin]  # only valid
        return {
            coin.symbol for coin in coins if coin  # get only symbol
        }

    def __getitem__(self, key):
        return self.raw[key]

    def __str__(self):
        out = "Transaction on " + str(self.date)
        out += str(self.coin_buy)
        out += str(self.coin_sell)
        if self.commission:
            out += "\nPaying " + str(self.commission.amount) + " " + \
                   str(self.commission.coin) + " as fee"

        out += "\nSuccessful? " + str(self.successful)

        return out


class Commission(Transaction):
    """ Transaction commission """

    def __init__(self, raw_dict, coin, date, successful=True):
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
            coin_in=None,
            coin_out=coin,
            date=date,
            trans_type=TransactionType.COMMISSION,
            successful=successful
        )

        self.coin = self.coin_sell
