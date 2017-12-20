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


""" Parse raw data """

import os

import pandas as pd


class Parser(object):
    """ Abstract parser """

    def __init__(self, input_file):
        """
        :param input_file: str
            File to parse
        """

        object.__init__(self)
        self.input_file = os.path.join(input_file)  # reformat file path
        self.is_csv = self.input_file.endswith(".csv")
        self.is_excel = self.input_file.endswith(".xlsx")

    def get_raw(self):
        """
        :return: pandas.DataFrame
            Read content of file
        """

        if self.is_excel:
            return pd.read_excel(self.input_file)
        elif self.is_csv:
            try:
                return pd.read_csv(self.input_file)
            except ValueError as e:
                if type(e) == pd.errors.ParserError:
                    return pd.read_csv(self.input_file, skiprows=2)
                else:
                    raise ValueError("File not supported!")
        else:
            raise ValueError("File not supported!")
