# !/usr/bin/python3
# coding: utf_8


""" Collect data from Gdax exchange """

from gdax import AuthenticatedClient as GdaxClient

from .models import ApiConfig


class GdaxApi(ApiConfig):
    """ Api config for GDAX exchange """

    def __init__(self, raw):
        ApiConfig.__init__(self, raw)

        self.passphrase = self.raw["passphrase"]

    def get_client(self):
        return GdaxClient(
            self.key,
            self.secret,
            self.passphrase
        )
