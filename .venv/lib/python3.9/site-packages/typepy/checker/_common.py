"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import decimal
import math


def isstring(value):
    return isinstance(value, (str,) + (str, bytes))


def isinf(value):
    try:
        return decimal.Decimal(value).is_infinite()
    except OverflowError:
        return True
    except TypeError:
        return False
    except (ValueError, decimal.InvalidOperation):
        return False


def isnan(value):
    try:
        return math.isnan(value)
    except (TypeError, OverflowError):
        return False
