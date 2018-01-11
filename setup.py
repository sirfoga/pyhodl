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


""" Setups library and install dependencies """

from setuptools import setup, find_packages

LITTLE_DESCRIPTION = "Framework to download, update, analyze and plot your " \
                     "crypto-transactions. Completely off-line and " \
                     "security-oriented."

DESCRIPTION = \
    "Pyhodl\n\n" + LITTLE_DESCRIPTION + "\n\
    Install\n\n\
    - $ python3 setup.py install  # from source\n\
    - $ pip3 install pyhodl  # via pip\n\
    \n\
    Questions and issues\n\n\
    The Github issue tracker is only for bug reports and feature requests.\n\
    License: Apache License Version 2.0, January 2004"

setup(
    name="pyhodl",
    version="0.2.7",
    author="sirfoga",
    author_email="sirfoga@protonmail.com",
    description=LITTLE_DESCRIPTION,
    long_description=DESCRIPTION,
    license="Apache License, Version 2.0",
    keywords="crypto hodl portfolio",
    url="https://github.com/sirfoga/pyhodl",
    packages=find_packages(exclude=["tests"]),
    package_data={"pyhodl": [".json", "pyhodl/data/raw/*.json"]},
    include_package_data=True,
    install_requires=[
        "matplotlib",
        "numpy",
        "xlrd",
        "pandas",
        "coinbase",
        "python-binance",
        "gdax",
        "ccxt",
        "pytz",
        "requests",
        "ciso8601",
        "scipy",
        "sklearn"
    ],
    entry_points={
        "console_scripts": ["pyhodl = pyhodl.cli:cli"]
    }
)
