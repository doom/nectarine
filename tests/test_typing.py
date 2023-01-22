from dataclasses import dataclass
from typing import List, Optional, OrderedDict, Union

from nectarine.typing import *


def test_is_number():
    assert is_number(int)
    assert is_number(float)

    assert not is_number(str)
    assert not is_number(bool)
    assert not is_number(List[str])


def test_is_primitive():
    assert is_primitive(int)
    assert is_primitive(float)
    assert is_primitive(str)
    assert is_primitive(bool)

    assert not is_primitive(dict)
    assert not is_primitive(list)
    assert not is_primitive(List[str])


def test_is_dataclass():
    @dataclass
    class ADataclass:
        pass

    class NotADataclass:
        pass

    assert is_dataclass(ADataclass)

    assert not is_dataclass(NotADataclass)
    assert not is_dataclass(int)


def test_is_generic():
    assert is_generic(Union[int, str])
    assert is_generic(Dict[str, int])

    assert not is_generic(str)


def test_is_union():
    assert is_union(Union[str, int])
    assert is_union(Optional[str])

    assert not is_union(int)


def test_is_optional():
    assert is_optional(Optional[int])
    assert not is_optional(int)
    assert not is_optional(Union[str, int])


def test_is_generic_collection():
    assert is_generic_collection(List[str])
    assert is_generic_collection(Tuple[str, int])
    assert is_generic_collection(Tuple[str, ...])
    assert not is_generic_collection(Union[str, int])


def test_is_linear_collection():
    assert is_linear_collection(List[str])
    assert is_linear_collection(Tuple[str, ...])

    assert not is_linear_collection(int)
    assert not is_linear_collection(Tuple[int, str])
    assert not is_linear_collection(Tuple[int])
    assert not is_linear_collection(Dict[str, int])


def test_is_mapping():
    assert is_mapping(Dict[str, int])
    assert is_mapping(OrderedDict[str, int])

    assert not is_mapping(int)
    assert not is_mapping(List[str])


def test_is_tuple():
    assert is_tuple(Tuple[int])
    assert is_tuple(Tuple[int, str])
    assert is_tuple(Tuple[int, ...])

    assert not is_tuple(int)
    assert not is_tuple(List[str])


def test_is_tuple_of_unknown_length():
    assert is_tuple_of_unknown_length(Tuple[int, ...])

    assert not is_tuple_of_unknown_length(Tuple[int])
    assert not is_tuple_of_unknown_length(Tuple[int, str])
    assert not is_tuple_of_unknown_length(int)
    assert not is_tuple_of_unknown_length(List[str])


def test_is_literal():
    assert is_literal(Literal[1])
    assert is_literal(Literal["some string"])
    assert not is_literal(int)
    assert not is_literal(List[str])


def test_is_parsable():
    class Parsable:
        @staticmethod
        def parse(self, value: str):
            pass

    class NotParsable:
        pass

    assert is_parsable(Parsable)
    assert not is_parsable(NotParsable)


def test_is_conform_to_hint():
    assert is_conform_to_hint(1, int)
    assert is_conform_to_hint(1, float)
    assert is_conform_to_hint(1., float)
    assert is_conform_to_hint("abc", str)
    assert is_conform_to_hint(None, Optional[str])
    assert is_conform_to_hint("abc", Union[str, int])
    assert is_conform_to_hint((1,2,3), Tuple[int, int, int])
    assert is_conform_to_hint((1,2,3), Tuple[int, ...])
    assert is_conform_to_hint([1,2,3], List[int])
    

    assert not is_conform_to_hint(1, str)
    assert not is_conform_to_hint(1., int)
    assert not is_conform_to_hint(1, str)
    assert not is_conform_to_hint(None, str)
    assert not is_conform_to_hint("abc", Union[float, int])
    assert not is_conform_to_hint((1,2,3), Tuple[int, int])
    assert not is_conform_to_hint(tuple('abc'), Tuple[int, ...])
    assert not is_conform_to_hint([1.2,3.2], List[int])
