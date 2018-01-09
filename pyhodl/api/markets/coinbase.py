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


""" Collect data from Coinbase exchange """

from coinbase.wallet.client import Client as CoinbaseClient

from .models import ApiConfig


class CoinbaseApi(ApiConfig):
    """ Api config for Coinbase exchange """

    def get_client(self):
        return CoinbaseClient(
            self.key,
            self.secret
        )
