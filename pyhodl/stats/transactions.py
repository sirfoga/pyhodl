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


""" Get transactions stats """
from pyhodl.data.parsers import build_exchanges
from pyhodl.updater.core import UpdateManager


def get_transactions_dates(exchanges):
    dates = [
        exchange.get_first_transaction().date for exchange in exchanges
    ]
    return sorted(dates)


def get_all_coins(exchanges):
    return [
        coin for exchange in exchanges
        for coin in exchange.build_wallets().keys()
    ]


def get_all_exchanges():
    folder_in = UpdateManager().get_data_folder()
    return list(build_exchanges(folder_in))
