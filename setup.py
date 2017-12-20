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

DESCRIPTION = \
    "Pyhodl\n\n\
    Static analysis of your crypto-transactions. Completely off-line and " \
    "security-oriented.\n\
    \n\
    Install\n\n\
    - $ python3 setup.py install  # from source\n\
    - $ pip3 install pyhodl  # via pip\n\
    \n\
    Questions and issues\n\n\
    The Github issue tracker is only for bug reports and feature requests.\n\
    License: Apache License Version 2.0, January 2004"

setup(
    name="pyhodl",
    version="0.2",
    author="sirfoga",
    author_email="sirfoga@protonmail.com",
    description="Static analysis of your crypto-transactions. Completely "
                "off-line and security-oriented",
    long_description=DESCRIPTION,
    license="Apache License, Version 2.0",
    keywords="crypto hodl portfolio",
    url="https://github.com/sirfoga/pyhodl",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "matplotlib",
        "numpy",
        "xlrd",
        "pandas"
    ]
)
