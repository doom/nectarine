"""
Module providing a ConfigurationProvider backed by a JSON file
"""

import json as _json

from nectarine.providers.dictionary import Dictionary


class Json(Dictionary):
    def __init__(self, file: str, must_exist: bool = True):
        try:
            with open(file, 'r') as f:
                value = _json.load(f)
        except FileNotFoundError:
            if must_exist:
                raise
            value = {}
        super().__init__(value)


def json(file: str, must_exist: bool = True):
    """
    Configure a provider that reads from a JSON file

    :param file:                        the path to the JSON file
    :param must_exist:                  whether or not the file must exist
    """
    return Json(file, must_exist)
