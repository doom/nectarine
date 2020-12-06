from dataclasses import dataclass
from typing import List, Tuple

import pytest

from nectarine.providers.arguments import arguments
from nectarine.errors import NectarineStrictLoadingError


@dataclass
class SimpleDataclass:
    option_a: str
    option_b: int


def test_simple_dataclass():
    provider = arguments(argv=["--option-a", "test", "--option-b", "123"])
    config = provider.load_configuration(SimpleDataclass)

    assert config["option_a"] == "test"
    assert config["option_b"] == 123
    assert len(config) == 2, "Ensuring no extra field is present"


def test_simple_strict_mode():
    provider = arguments(argv=["--option-a", "test", "--option-b", "123"])
    config = provider.load_configuration(SimpleDataclass, strict=True)
    assert config["option_a"] == "test"
    assert config["option_b"] == 123
    assert len(config) == 2, "Ensuring no extra field is present"

    with pytest.raises(NectarineStrictLoadingError):
        provider = arguments(argv=["--option-a", "test", "--option-b", "123", "--unknown-option", "nope"])
        provider.load_configuration(SimpleDataclass, strict=True)


@dataclass
class NestedDataclass:
    nested: SimpleDataclass
    option_c: int


def test_nested_dataclass():
    provider = arguments(argv=["--nested-option-a", "test", "--nested-option-b", "123", "--option-c", "456"])
    config = provider.load_configuration(NestedDataclass)

    assert config["nested"]["option_a"] == "test"
    assert config["nested"]["option_b"] == 123
    assert config["option_c"] == 456
    assert len(config) == 2 and len(config["nested"]) == 2, "Ensuring no extra field is present"


@dataclass
class DataclassWithTuple:
    coordinates: Tuple[int, int]


def test_dataclass_with_tuple():
    provider = arguments(argv=["--coordinates", "1", "2"])
    config = provider.load_configuration(DataclassWithTuple)

    assert config["coordinates"][0] == 1
    assert config["coordinates"][1] == 2
    assert len(config) == 1 and len(config["coordinates"]) == 2, "Ensuring no extra field is present"


@dataclass
class DataclassWithList:
    values: List[int]


def test_dataclass_with_list():
    provider = arguments(argv=["--values", "1", "--values", "2", "--values", "3"])
    config = provider.load_configuration(DataclassWithList)

    assert config["values"][0] == 1
    assert config["values"][1] == 2
    assert config["values"][2] == 3
    assert len(config) == 1 and len(config["values"]) == 3, "Ensuring no extra field is present"


@dataclass
class DataclassWithBool:
    a_flag: bool


def test_dataclass_with_bool():
    provider = arguments(argv=["--a-flag"])
    config = provider.load_configuration(DataclassWithBool)

    assert config["a_flag"] is True
