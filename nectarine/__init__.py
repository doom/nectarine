"""
Main Nectarine module
"""

from functools import reduce
from typing import Any, Callable, Dict, List, Type

from nectarine.configuration_provider import ConfigurationProvider
from nectarine.dataclasses import dataclass_from_dict
from nectarine.providers.env import env
from nectarine.providers.arguments import arguments
from nectarine.providers.dictionary import dictionary
from nectarine.providers.json import json

Merger = Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
MergeStrategy = Callable[[str, Any, Any, Merger], Any]


def _merge_by_merging_containers_or_replacing(_: str, value1: Any, value2: Any, merge: Merger):
    if isinstance(value1, dict) and isinstance(value2, dict):
        return merge(value1, value2)
    if isinstance(value1, list) and isinstance(value2, list):
        return value1 + value2
    return value2


def _merge_dicts(lh_dict: Dict[str, Any], rh_dict: Dict[str, Any], strategy: MergeStrategy) -> Dict[str, Any]:
    for key, rh_value in rh_dict.items():
        lh_value = lh_dict.get(key)
        if lh_value is None:
            lh_dict[key] = rh_value
        else:
            lh_dict[key] = _merge_by_merging_containers_or_replacing(
                key,
                lh_value,
                rh_value,
                lambda a, b: _merge_dicts(a, b, strategy)
            )
    return lh_dict


def load(
        target: Type,
        providers: List[ConfigurationProvider],
        strict: bool = False,
):
    """
    Load a dataclass instance using the given providers

    :param target:                      the target dataclass type
    :param providers:                   the list of providers to use, in order of priority
    :param strict:                      activate strict mode (reject extra values, ...)
    """
    results = []
    for provider in reversed(providers):
        r = provider.load_configuration(target, strict=strict)
        results.append(r)
    result = reduce(lambda acc, new: _merge_dicts(acc, new, _merge_by_merging_containers_or_replacing), results, {})
    return dataclass_from_dict(target, result)
