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


""" Plot balances data with trends and stats """

from ..data.core import BalancesParser


class Plotter(object):
    """ Plots data """

    def __init__(self, input_file):
        """
        :param input_file: str
            File to parse
        """

        self.data = BalancesParser(input_file).balances

    def plot_qty(self):
        """
        :return:
        """

        pass

    def plot_equiv(self):
        """
        :return:
        """

        pass

    def plot_total_equiv(self):
        """
        :return:
        """

        pass

    def plot(self):
        """
        :return:
        """

        pass
