from contextlib import contextmanager
from dataclasses import dataclass
import os
from typing import List, Tuple

from nectarine.providers.env import env


@contextmanager
def push_env(**kwargs):
    old_env = os.environ.copy()
    for k, v in kwargs.items():
        os.environ[k] = v
    try:
        yield
    finally:
        os.environ = old_env


@dataclass
class SimpleDataclass:
    option_a: str
    option_b: int


def test_simple_dataclass():
    with push_env(OPTION_A="test", OPTION_B="123"):
        provider = env()
        config = provider.load_configuration(SimpleDataclass)

        assert config["option_a"] == "test"
        assert config["option_b"] == 123
        assert len(config) == 2, "Ensuring no extra field is present"


@dataclass
class NestedDataclass:
    nested: SimpleDataclass
    option_c: int


def test_nested_dataclass():
    with push_env(NESTED_OPTION_A="test", NESTED_OPTION_B="123", OPTION_C="456"):
        provider = env()
        config = provider.load_configuration(NestedDataclass)

        assert config["nested"]["option_a"] == "test"
        assert config["nested"]["option_b"] == 123
        assert config["option_c"] == 456
        assert len(config) == 2 and len(config["nested"]) == 2, "Ensuring no extra field is present"


@dataclass
class DataclassWithList:
    values: List[int]
    opt: int


def test_dataclass_with_list():
    with push_env(VALUES="1,2,3", OPT="1"):
        provider = env(allow_lists=True)
        config = provider.load_configuration(DataclassWithList)

        assert config["values"][0] == 1
        assert config["values"][1] == 2
        assert config["values"][2] == 3
        assert len(config) == 2 and len(config["values"]) == 3, "Ensuring no extra field is present"


def test_dataclass_with_list_without_allowing():
    with push_env(VALUES="1,2,3", OPT="1"):
        provider = env(allow_lists=False)
        config = provider.load_configuration(DataclassWithList)
        assert len(config) == 1  # lists are ignored
        assert config["opt"] == 1
