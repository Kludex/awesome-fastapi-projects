"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import re
from typing import Any, Optional, Type

from ._const import StrictLevel
from .type import AbstractType, Integer, NullString, RealNumber, String


def is_hex(value: Any) -> bool:
    try:
        int(value, 16)
    except (TypeError, ValueError):
        return False

    return True


def is_null_string(value: Any) -> bool:
    return NullString(value, strict_level=StrictLevel.MIN).is_type()


def is_not_null_string(value: Any) -> bool:
    return String(value, strict_level=StrictLevel.MAX).is_type()


def is_empty_sequence(value: Any) -> bool:
    try:
        return value is None or len(value) == 0
    except TypeError:
        return False


def is_not_empty_sequence(value: Any) -> bool:
    try:
        return len(value) > 0
    except TypeError:
        return False


def extract_typepy_from_dtype(dtype) -> Optional[Type[AbstractType]]:
    dtype = str(dtype)

    if re.search("^float", dtype):
        return RealNumber

    if re.search("^int", dtype):
        return Integer

    return None
