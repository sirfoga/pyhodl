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


""" Parser prices, market cap data and values downloaded with this app """

import abc

from hal.files.parsers import JSONParser


class AbstractDatetimeTable(JSONParser):
    """ Get content from file and load a datetime-based database """

    def __init__(self, input_file):
        JSONParser.__init__(self, input_file)

        self.content = self.get_content()

    @abc.abstractmethod
    def get_values_on(self, dt):
        """
        :param dt: datetime
            Date to get values of
        :return: {}
            Value on date
        """

        return

    @abc.abstractmethod
    def get_values_between(self, since, until):
        """
        :param since: datetime
            Get values since this date
        :param until: datetime
            Get values until this date
        :return: [] of {}
            Get all values if key is date in between
        """

        return


class MarketcapData:
    """ Parse market cap data """
