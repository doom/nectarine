"""
Module providing typing utilities on top of those from the typing module
"""

from inspect import getattr_static
import typing
from typing import Any, Collection, Dict, FrozenSet, List, Mapping, Set, Tuple, Type, Union


def is_number(type_: Type) -> bool:
    """
    Check whether a type is a number type

    :param type_:                       the type to check
    """
    return type_ in {int, float}


def is_primitive(type_: Type) -> bool:
    """
    Check whether a type is a primitive type

    :param type_:                       the type to check
    """
    return type_ in {bool, int, float, str}


def is_dataclass(type_: Type) -> bool:
    """
    Check whether a type is a dataclass

    :param type_:                       the type to check
    """
    return hasattr(type_, '__dataclass_fields__')


def is_generic(type_: Type) -> bool:
    """
    Check whether a type is a generic

    :param type_:                       the type to check
    """
    return typing.get_origin(type_) is not None


def get_generic_args(type_: Type) -> Tuple[Type, ...]:
    """
    Retrieve the arguments of a generic type

    :param type_:                       the generic type to retrieve the arguments from
    """
    assert is_generic(type_)
    return typing.get_args(type_)


def is_union(type_: Type) -> bool:
    """
    Check whether a type is a union, i.e. it is of the form Union[Ts] where Ts is a list of types

    :param type_:                       the type to check
    """
    return is_generic(type_) and typing.get_origin(type_) is Union


def is_optional(type_: Type) -> bool:
    """
    Check whether a type is an optional, i.e. it is of the form Optional[T] where T is a type

    :param type_:                       the type to check
    """
    if not is_union(type_):  # Since Optional[T] is actually Union[T, None], we check that
        return False
    args = get_generic_args(type_)
    return len(args) == 2 and isinstance(None, args[1])


def is_generic_collection(type_: Type) -> bool:
    """
    Check whether a type is a generic collection

    :param type_:                       the type to check
    """
    if not is_generic(type_):
        return False
    origin = typing.get_origin(type_)
    try:
        return origin is not None and issubclass(origin, Collection)
    except TypeError:  # Other generics such as Union have an origin that cannot be passed to issubclass
        return False


def get_generic_collection_origin(type_: Type) -> Type:
    """
    Retrieve the origin of a collection type

    :param type_:                       the generic collection type to retrieve the origin from
    """
    return typing.get_origin(type_)


def is_linear_collection(type_: Type) -> bool:  # Quite unsure of this wording
    """
    Check whether a type is a "linear" collection, i.e. a generic collection parametrized by a single type

    :param type_:                       the type to check
    """
    return is_generic_collection(type_) and \
           ((len(get_generic_args(type_)) == 1 and not is_tuple(type_)) or is_tuple_of_unknown_length(type_))


def is_mapping(type_: Type) -> bool:
    """
    Check whether a type is a mapping

    :param type_:                       the type to check
    """
    return is_generic_collection(type_) and issubclass(get_generic_collection_origin(type_), Mapping)


def is_tuple(type_: Type) -> bool:
    """
    Check whether a type is a tuple

    :param type_:                       the type to check
    """
    return is_generic(type_) and typing.get_origin(type_) is tuple


def is_tuple_of_unknown_length(type_: Type) -> bool:
    """
    Check whether a type is a tuple of unknown length, i.e. it is of the form Tuple[T, ...] where T is a type

    :param type_:                       the type to check
    """
    if not is_tuple(type_):
        return False
    args = get_generic_args(type_)
    return len(args) == 2 and args[1] is Ellipsis


def is_parsable(type_: Type) -> bool:
    """
    Check whether a type is parsable from a string, i.e. it has a static "parse" method

    :param type_:                       the type to check
    """
    parse = getattr_static(type_, "parse", None)
    return isinstance(parse, staticmethod)


def is_conform_to_hint(value, hint: Type) -> bool:
    """
    Check whether a value can satisfy a given type hint

    :param value:                       the value
    :param hint:                        the type hint
    """
    if hint is Any:
        return True
    if is_optional(hint):
        arg = get_generic_args(hint)[0]
        return value is None or is_conform_to_hint(value, arg)
    if is_union(hint):
        allowed_types = get_generic_args(hint)
        return any(is_conform_to_hint(value, allowed_type) for allowed_type in allowed_types)
    if is_generic_collection(hint):
        origin = typing.get_origin(hint)
        if not isinstance(value, origin):
            return False
        args = get_generic_args(hint)
        if issubclass(origin, Mapping):
            key_type = args[0]
            value_type = args[1]
            return all(is_conform_to_hint(k, key_type) and is_conform_to_hint(v, value_type) for k, v in value.items())
        if origin is tuple:
            if is_tuple_of_unknown_length(hint):
                value_type = args[1]
                return all(is_conform_to_hint(v, value_type) for v in value)
            else:
                return len(args) == len(value) and all(is_conform_to_hint(v, h) for v, h in zip(value, args))
        assert len(args) == 1
        value_type = args[0]
        return all(is_conform_to_hint(v, value_type) for v in value)
    if hint is float:
        return isinstance(value, (int, float))
    if is_dataclass(hint) and isinstance(value, dict):
        return True
    return isinstance(value, hint)


def hintify(type_: Type) -> Type:
    """
    Convert a real type into an appropriate type hint (or leave it unchanged, if not needed)

    :param type_:                       the type to hintify
    """
    # XXX: this clearly isn't ideal
    types = {
        list: List[Any],
        set: Set[Any],
        frozenset: FrozenSet[Any],
        tuple: Tuple[Any, ...],
        dict: Dict[Any, Any]
    }
    return types.get(type_) or type_
