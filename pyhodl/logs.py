# !/usr/bin/python3
# coding: utf_8


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
