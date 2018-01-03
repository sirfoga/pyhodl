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


""" Test pyhodl.data module """

import unittest

from pyhodl.config import FIAT_COINS
from pyhodl.data.coins import Coin, CryptoCoin


class TestCoins(unittest.TestCase):
    """ Basic test class to test pyhodl.data.coins module"""

    def test_eq(self):
        """ The actual test. Any method which starts with ``test_`` will
        considered as a test case.
        """

        symbol = "USD"
        coin = Coin(symbol)
        crypto_coin = Coin(symbol)
        self.assertTrue(symbol == coin == crypto_coin)

    def test_eq_crypto(self):
        """ The actual test. Any method which starts with ``test_`` will
        considered as a test case.
        """

        btc = CryptoCoin("btc", "bitcoin")
        bch = CryptoCoin("bch", "bitcoin-cash")
        self.assertFalse(btc == bch)

        btc_malformed = CryptoCoin(
            "bt?", name="bitcoin", other_names=["bitcoin"]
        )
        self.assertTrue(btc == btc_malformed)

        btc_very_malformed = CryptoCoin(
            "bt?", name="b--", other_names=["bitcoin"]
        )
        self.assertTrue(btc == btc_very_malformed)
        self.assertTrue(btc_malformed == btc_very_malformed)

        btc_malformed.symbol = "btcccccc"
        self.assertTrue(btc_malformed == btc_very_malformed)

    def test_in(self):
        self.assertTrue("usd" in FIAT_COINS)
        self.assertTrue("USD" in FIAT_COINS)
        self.assertTrue(Coin("usd") in FIAT_COINS)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
