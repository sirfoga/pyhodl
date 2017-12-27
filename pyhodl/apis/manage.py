""" Manage your APIs: add, edit, remove exchanges API """

import os

from hal.files.parsers import JSONParser
from hal.files.save_as import write_dicts_to_json

API_CONFIG_FILE = os.path.join(
    os.getenv("HOME"),
    ".pyhodl",
    "config",
    "api"
)


class ApiManager:
    """ Manages your secrets """

    def __init__(self, config_file=API_CONFIG_FILE):
        """
        :param config_file: str
            Path to config file
        """

        self.config_file = config_file
        self.raw = None
        self.data = {}
        self._read_config()

    def _read_config(self):
        """
        :return: {}
            Config data
        """

        self.raw = JSONParser(self.config_file).get_content()
        for key, value in self.raw.items():
            self.data[key] = ApiConfig(value)

    def create_config(self):
        """
        :return: void
            Creates config file
        """

        if os.path.exists(self.config_file):
            raise ValueError("Creating new config will erase previous data!")

        write_dicts_to_json({}, self.config_file)  # empty data

    def get(self, api_name):
        """
        :param api_name: str
            Api name
        :return: {}
            Api config
        """

        return self.data[api_name]

    def add(self, api_name, key, secret):
        self.data[api_name] = ApiConfig({
            "key": key,
            "secret": secret
        })

    def save(self):
        out = {}
        for key, value in self.data.items():
            out[key] = value.to_dict()

        write_dicts_to_json(out, self.config_file)


class ApiConfig:
    """ Config of API """

    def __init__(self, raw):
        """
        :param raw: {}
            Raw data
        """

        self.raw = raw
        self.key = raw["key"]
        self.secret = raw["secret"]

    def edit(self, new_key, new_secret):
        self.key = new_key
        self.secret = new_secret

    def to_dict(self):
        return self.raw
