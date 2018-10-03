# !/usr/bin/python3
# coding: utf_8


""" Test pyhodl.data module """

import unittest

from pyhodl.data.coins import Coin, CryptoCoin, FIAT_COINS


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
        self.assertTrue("BTC" == Coin("BTC"))
        self.assertTrue("BTC" == CryptoCoin("BTC"))


def main():
    unittest.main()


if __name__ == '__main__':
    main()
