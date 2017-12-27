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


""" Updates exchange transactions """

import os

from .app import DATA_FOLDER, ConfigManager

UPDATE_CONFIG = os.path.join(
    DATA_FOLDER,
    "config.json"
)


class UpdateManager(ConfigManager):
    """ Manages config for Updater """

    def __init__(self):
        ConfigManager.__init__(self, UPDATE_CONFIG)


class Updater:
    """ Updates exchanges local data """

    def __init__(self):
        self.manager = UpdateManager()

    def run(self):
        pass
