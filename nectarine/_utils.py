"""
Internal module providing helper functions
"""

from typing import Any, Dict, Type
from nectarine.errors import NectarineInvalidValueError


def insert_at_path(d: Dict[str, Any], path, value: Any):
    first, *remaining = path
    if remaining:
        if first not in d:
            d[first] = {}
        insert_at_path(d[first], remaining, value)
    else:
        d[first] = value


def try_convert(value, type_: Type):
    try:
        return type_(value)
    except ValueError:
        raise NectarineInvalidValueError(type_, value)
