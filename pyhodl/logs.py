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


""" Log stuff """

from datetime import datetime

from .utils.misc import get_actual_class_name

LOG_TIME_FORMAT = "%H:%M:%S"


class Logger:
    """ Logs itself """

    def __init__(self):
        self.class_name = get_actual_class_name(self)

    def log(self, *content):
        """
        :param content: *
            Data to print to stdout
        :return: void
            Prints log
        """

        print(datetime.now().strftime(LOG_TIME_FORMAT), self.class_name,
              ">>>", " ".join([str(x) for x in content]))
