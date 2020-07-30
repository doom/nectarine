"""
Module providing exception types to describe errors occurring when loading a configuration
"""

from typing import List, Type


class NectarineError(Exception):
    """
    Base class for all the exceptions raised by Nectarine
    """


class NectarineStrictLoadingError(NectarineError):
    """
    Exception class representing an error related to extraneous keys when using strict loading
    """

    def __init__(self, offending_keys: List[str]):
        self.offending_keys = offending_keys

    def __str__(self):
        keys = (f"""'{".".join(x)}'""" for x in self.offending_keys)
        return f"found extraneous keys: {', '.join(keys)}"


class NectarineInvalidValueError(NectarineError):
    """
    Exception class representing an error related to an invalid value
    """

    def __init__(self, expected_type: Type, value):
        self.expected_type = expected_type
        self.value = value

    def __str__(self):
        return f"expected an instance of type '{self.expected_type}', got '{self.value}' of type '{type(self.value).__name__}'"


class NectarineMissingValueError(NectarineError):
    """
    Exception class representing an error related to a missing value
    """

    def __init__(self, missing_key: str):
        self.missing_key = missing_key

    def __str__(self):
        return f"missing value for key '{self.missing_key}'"
