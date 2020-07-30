"""
Module providing a ConfigurationProvider backed by a YAML file
"""

import yaml as _yaml

from nectarine.providers.dictionary import Dictionary


class Yaml(Dictionary):
    def __init__(self, file: str, must_exist: bool = True):
        try:
            with open(file, 'r') as f:
                value = _yaml.safe_load(f)
        except FileNotFoundError:
            if must_exist:
                raise
            value = {}
        super().__init__(value)


def yaml(file: str, must_exist: bool = True):
    """
    Configure a provider that reads from a YAML file

    :param file:                        the path to the YAML file
    :param must_exist:                  whether or not the file must exist
    """
    return Yaml(file, must_exist)
