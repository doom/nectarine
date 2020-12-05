"""
Module providing a ConfigurationProvider backed by a Python dictionary
"""

from typing import Any, Dict, List, Tuple, Type

from nectarine.configuration_provider import ConfigurationProvider, Path
from nectarine.dataclasses import get_paths
from nectarine.errors import NectarineStrictLoadingError, NectarineInvalidValueError
from nectarine.typing import is_conform_to_hint, is_dataclass, is_tuple
from nectarine._utils import insert_at_path


def _get_dict_paths(d: Dict[str, Any], path=()):
    for k, v in d.items():
        yield (*path, k), v
        if isinstance(v, dict):
            yield from _get_dict_paths(v, (*path, k))


def _unify_paths(paths: Dict, dict_paths: Dict) -> Tuple[Dict, List[Path]]:
    result = {}
    extraneous = []
    for k, v in dict_paths.items():
        if k in paths:
            result[k] = (paths[k], v)
        else:
            parent = k[:-1]
            if parent == () or (parent in paths and is_dataclass(paths[parent].type)):
                extraneous.append(k)
    return result, extraneous


class Dictionary(ConfigurationProvider):
    def __init__(self, value: Dict[str, Any]):
        self.value = value

    def load_configuration(self, target_type: Type, strict=False) -> Dict[str, Any]:
        paths = dict(get_paths(target_type))
        dict_paths = dict(_get_dict_paths(self.value))
        unified, extraneous = _unify_paths(paths, dict_paths)
        if strict is True and extraneous:
            raise NectarineStrictLoadingError(offending_keys=extraneous)
        result = {}
        for path, (field, value) in unified.items():
            if not is_dataclass(field.type):
                if isinstance(value, list) and is_tuple(field.type):
                    value = tuple(value)
                if is_conform_to_hint(value, field.type):
                    insert_at_path(result, path, value)
                else:
                    raise NectarineInvalidValueError(expected_type=field.type, value=value)
        return result


def dictionary(value: Dict[str, Any]):
    """
    Configure a provider that reads from a dictionary

    :param value:                       the dictionary to extract data from
    """
    return Dictionary(value)
