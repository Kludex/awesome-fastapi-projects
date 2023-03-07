"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import copy
import itertools
from decimal import Decimal
from typing import Mapping, Union

from typepy import StrictLevel, Typecode

from .typing import StrictLevelMap


NOT_QUOTING_FLAGS = {
    Typecode.BOOL: False,
    Typecode.DATETIME: False,
    Typecode.DICTIONARY: False,
    Typecode.INFINITY: False,
    Typecode.INTEGER: False,
    Typecode.IP_ADDRESS: False,
    Typecode.LIST: False,
    Typecode.NAN: False,
    Typecode.NULL_STRING: False,
    Typecode.NONE: False,
    Typecode.REAL_NUMBER: False,
    Typecode.STRING: False,
}

MAX_STRICT_LEVEL_MAP = dict(itertools.product(list(Typecode), [StrictLevel.MAX]))
MIN_STRICT_LEVEL_MAP = dict(itertools.product(list(Typecode), [StrictLevel.MIN]))


class DefaultValue:
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
    FLOAT_TYPE = Decimal
    INF_VALUE = FLOAT_TYPE("inf")
    NAN_VALUE = FLOAT_TYPE("nan")

    QUOTING_FLAGS = copy.deepcopy(NOT_QUOTING_FLAGS)

    STRICT_LEVEL_MAP: StrictLevelMap = {
        "default": StrictLevel.MAX,
        Typecode.BOOL: StrictLevel.MAX,
        Typecode.DATETIME: StrictLevel.MAX,
        Typecode.DICTIONARY: StrictLevel.MAX,
        Typecode.REAL_NUMBER: 1,
        Typecode.INFINITY: StrictLevel.MIN,
        Typecode.INTEGER: 1,
        Typecode.IP_ADDRESS: StrictLevel.MAX,
        Typecode.LIST: StrictLevel.MAX,
        Typecode.NAN: StrictLevel.MIN,
        Typecode.NONE: StrictLevel.MAX,
        Typecode.NULL_STRING: StrictLevel.MIN,
        Typecode.STRING: StrictLevel.MIN,
    }

    TYPE_VALUE_MAP: Mapping[Typecode, Union[float, Decimal, None]] = {
        Typecode.NONE: None,
        Typecode.INFINITY: INF_VALUE,
        Typecode.NAN: NAN_VALUE,
    }

    MAX_WORKERS = 1
    MAX_PRECISION = 100


def default_datetime_formatter(value):
    return value.strftime(DefaultValue.DATETIME_FORMAT)
