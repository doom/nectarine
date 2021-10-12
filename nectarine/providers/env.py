"""
Module providing a ConfigurationProvider backed by the program environment
"""

import os
from typing import Any, Callable, Dict, Type

from nectarine.configuration_provider import ConfigurationProvider, Path
from nectarine.dataclasses import get_paths
from nectarine.errors import NectarineInvalidValueError
from nectarine.typing import get_generic_args, get_generic_collection_origin, \
    is_number, is_linear_collection, is_tuple, is_parsable, is_literal
from nectarine._utils import insert_at_path, try_convert


def path_to_variable_name(path: Path) -> str:
    name = '_'.join(path).upper()
    return name


class Env(ConfigurationProvider):
    DEFAULT_SUPPORTED_TYPES = {int, float, bool, str}

    def __init__(
            self,
            prefix: str = None,
            allow_lists: bool = False,
            list_separator: str = ',',
            variable_name_converter: Callable[[Path], str] = None,
    ):
        self.prefix = prefix
        self.allow_lists = allow_lists
        self.list_separator = list_separator
        self.variable_name_converter = variable_name_converter or path_to_variable_name

    def is_supported_type(self, type_: Type):
        if type_ in self.DEFAULT_SUPPORTED_TYPES:
            return True
        if is_literal(type_):
            return True
        if is_parsable(type_):
            return True
        return self.allow_lists and (is_linear_collection(type_) or is_tuple(type_))

    def convert_to(self, target_type: Type, value: str):
        if target_type is Any:
            return value
        if is_number(target_type):
            return try_convert(value, target_type)
        if is_linear_collection(target_type):
            origin = get_generic_collection_origin(target_type)
            value_type = get_generic_args(target_type)[0]
            return origin(try_convert(v, value_type) for v in value.split(self.list_separator))
        if is_tuple(target_type):
            args = get_generic_args(target_type)
            values = value.split(self.list_separator)
            if len(args) != len(values):
                raise NectarineInvalidValueError(target_type, value)
            return tuple(try_convert(v, t) for v, t in zip(values, args))
        if is_literal(target_type):
            allowed_values = get_generic_args(target_type)
            for v in allowed_values:
                try:
                    converted_value = type(v)(value)
                    if converted_value == v:
                        return converted_value
                except ValueError:
                    pass
            raise NectarineInvalidValueError(target_type, value)
        return value

    def load_configuration(self, target_type: Type, strict=False) -> Dict[str, Any]:
        paths = ((path, field) for path, field in get_paths(target_type) if self.is_supported_type(field.type))
        result = {}
        for path, field in paths:
            var_name = self.variable_name_converter(path)
            if self.prefix is not None:
                var_name = self.prefix + var_name
            value = os.environ.get(var_name)
            if value is not None:
                value = self.convert_to(field.type, value)
                insert_at_path(result, path, value)
        return result


def env(
        prefix: str = None,
        allow_lists: bool = False,
        list_separator: str = ',',
        variable_name_converter: Callable[[Path], str] = None,
):
    """
    Configure a provider that reads from the program environment

    :param prefix:                      the prefix to use for each environment variable name (or None for no prefix)
    :param allow_lists:                 whether or not lists should be parsed from environment variables
    :param list_separator:              the separator to use to split values when parsing lists
    :param variable_name_converter:     the function used to generate variable names from paths
    """
    return Env(
        prefix=prefix,
        allow_lists=allow_lists,
        list_separator=list_separator,
        variable_name_converter=variable_name_converter,
    )
