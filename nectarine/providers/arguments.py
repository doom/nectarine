"""
Module providing a ConfigurationProvider backed by the program arguments
"""

import argparse
import sys
from typing import Any, Callable, Dict, List, Tuple, Type

from nectarine.configuration_provider import ConfigurationProvider, Path
from nectarine.dataclasses import get_paths
from nectarine.errors import NectarineStrictLoadingError
from nectarine.typing import is_primitive, is_tuple, is_linear_collection, is_parsable, \
    get_generic_args
from nectarine._utils import insert_at_path, try_convert


def _make_tuple_action(types: Tuple[Type]):
    class TupleAction(argparse.Action):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.tuple_types = types

        def __call__(self, parser, namespace, values, option_string=None):
            assert len(values) == len(self.tuple_types)
            values = tuple(try_convert(v, t) for v, t in zip(values, self.tuple_types))
            setattr(namespace, self.dest, values)

    return TupleAction


def path_to_flag_name(path: Path) -> str:
    name = '-'.join(path).replace('_', '-')
    return name


def _is_supported_type(type_: Type) -> bool:
    if is_primitive(type_):
        return True
    if is_linear_collection(type_):
        value_type = get_generic_args(type_)[0]
        return is_primitive(value_type) or is_parsable(value_type)
    if is_tuple(type_):
        values_types = get_generic_args(type_)
        return all(is_primitive(t) for t in values_types)
    return False


def _add_argument_for(parser: argparse.ArgumentParser, name, field):
    kwargs = {"metavar": "[value]", "required": False}
    if field.type is bool:
        parser.add_argument(f"--{name}", action='store_true', required=False)
    elif is_primitive(field.type):
        parser.add_argument(f"--{name}", type=lambda x: try_convert(x, field.type), **kwargs)
    elif is_linear_collection(field.type):
        value_type = get_generic_args(field.type)[0]
        if is_primitive(value_type):
            parser.add_argument(f"--{name}", action='append', type=lambda x: try_convert(x, value_type), **kwargs)
        else:
            assert is_parsable(value_type)
            parser.add_argument(f"--{name}", action='append', type=str, **kwargs)
    elif is_tuple(field.type):  # This is matched only for fixed-length tuples
        values_types = get_generic_args(field.type)
        parser.add_argument(f"--{name}", nargs=len(values_types), action=_make_tuple_action(values_types), **kwargs)


class Arguments(ConfigurationProvider):

    def __init__(
            self,
            argv: List[str] = None,
            flag_name_converter: Callable[[Path], str] = None,
    ):
        self.argv = argv if argv is not None else sys.argv[1:]
        self.variable_name_converter = flag_name_converter or path_to_flag_name

    def load_configuration(self, target_type: Type, strict=False) -> Dict[str, Any]:
        parser = argparse.ArgumentParser(allow_abbrev=False, add_help=True)
        paths = ((path, field) for path, field in get_paths(target_type) if _is_supported_type(field.type))
        arg_to_path = {}
        for path, field in paths:
            arg_name = self.variable_name_converter(path)
            arg_to_path[arg_name] = path
            _add_argument_for(parser, arg_name, field)
        args, unknown = parser.parse_known_args(self.argv)
        if unknown:
            raise NectarineStrictLoadingError(offending_keys=unknown)
        result = {}
        for arg_name, value in vars(args).items():
            if value is not None:
                insert_at_path(result, arg_to_path[arg_name.replace('_', '-')], value)
        return result


def arguments(
        argv: List[str] = None,
        flag_name_converter: Callable[[Path], str] = None,
):
    """
    Configure a provider that reads from the program arguments

    :param argv:                    the argument vector to parse from
    :param flag_name_converter:     the function used to generate flag names from paths
    """
    return Arguments(
        argv=argv,
        flag_name_converter=flag_name_converter
    )
