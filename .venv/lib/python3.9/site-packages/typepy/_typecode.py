"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import enum


@enum.unique
class Typecode(enum.Enum):
    NONE = 0
    INTEGER = 1 << 0
    REAL_NUMBER = 1 << 1
    STRING = 1 << 2
    NULL_STRING = 1 << 3
    DATETIME = 1 << 4
    INFINITY = 1 << 5
    NAN = 1 << 6
    BOOL = 1 << 7
    DICTIONARY = 1 << 8
    LIST = 1 << 9
    IP_ADDRESS = 1 << 10
    BYTES = 1 << 11
