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


""" Config your app """

import os

APP_NAME = "Pyhodl"
APP_SHORT_NAME = "pyhodl"

HOME_FOLDER = os.getenv("HOME")
APP_FOLDER = os.path.join(
    HOME_FOLDER,
    APP_SHORT_NAME
)
API_FOLDER = "api"
DATA_FOLDER = "data"


def create_workplace():
    """
    :return: void
        Creates folder
    """

    os.makedirs(APP_FOLDER)
    for directory in [APP_FOLDER, DATA_FOLDER]:
        os.makedirs(
            os.path.join(
                APP_FOLDER,
                directory
            )
        )
