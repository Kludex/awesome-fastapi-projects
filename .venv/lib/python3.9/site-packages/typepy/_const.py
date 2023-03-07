"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from decimal import Decimal


class DefaultValue:
    FLOAT_TYPE = Decimal
    STRIP_ANSI_ESCAPE = True


class StrictLevel:
    MIN = 0
    MAX = 100


class ParamKey:
    STRIP_ANSI_ESCAPE = "strip_ansi_escape"
    TIMEZONE = "timezone"
