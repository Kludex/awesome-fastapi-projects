"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import re
from decimal import Decimal

from ._checker import CheckerFactory, TypeCheckerBase, TypeCheckerDelegator
from ._common import isinf, isnan, isstring


RE_E = re.compile("[eE]")
RE_SCIENTIFIC_NOTATION = re.compile(r"^-?\d+(?:\.\d*)?[eE][+\-]?\d{,2}$")


class RealNumberTypeCheckerStrictLevel0(TypeCheckerBase):
    def is_instance(self):
        return isinstance(self._value, (float, Decimal))

    def is_exclude_instance(self):
        return isinstance(self._value, bool) or isnan(self._value) or isinf(self._value)

    def is_valid_after_convert(self, converted_value):
        return not isinf(converted_value) and not isnan(converted_value)


class RealNumberTypeCheckerStrictLevel1(RealNumberTypeCheckerStrictLevel0):
    def is_instance(self):
        return super().is_instance() and not float(self._value).is_integer()

    def is_exclude_instance(self):
        if (
            isinstance(self._value, str)
            and RE_E.search(self._value)
            and RE_SCIENTIFIC_NOTATION.search(self._value) is None
        ):
            return True

        return isinstance(self._value, int) or super().is_exclude_instance()

    def is_valid_after_convert(self, converted_value):
        return not float(converted_value).is_integer()


class RealNumberTypeCheckerStrictLevel2(RealNumberTypeCheckerStrictLevel1):
    def is_exclude_instance(self):
        return super().is_exclude_instance() or isstring(self._value)


_factory = CheckerFactory(
    checker_mapping={
        0: RealNumberTypeCheckerStrictLevel0,
        1: RealNumberTypeCheckerStrictLevel1,
        2: RealNumberTypeCheckerStrictLevel2,
    }
)


class RealNumberTypeChecker(TypeCheckerDelegator):
    def __init__(self, value, strict_level):
        super().__init__(value=value, checker_factory=_factory, strict_level=strict_level)
