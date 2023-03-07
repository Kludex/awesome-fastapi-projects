"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import re
from decimal import Decimal

from ._checker import CheckerFactory, TypeCheckerBase, TypeCheckerDelegator
from ._common import isinf, isnan


RE_SCIENTIFIC_NOTATION = re.compile(r"^-?\d+(?:\.\d*)?[eE][+\-]?\d{3,}$")


class IntegerTypeCheckerStrictLevel0(TypeCheckerBase):
    def is_instance(self):
        if isinstance(self._value, int):
            return not isinstance(self._value, bool)

        if isinstance(self._value, (float, Decimal)):
            return True

        return False

    def is_exclude_instance(self):
        return isnan(self._value) or isinf(self._value)


class IntegerTypeCheckerStrictLevel1(IntegerTypeCheckerStrictLevel0):
    def is_instance(self):
        if not super().is_instance():
            return False

        if isinstance(self._value, (float, Decimal)):
            if float(self._value).is_integer():
                return True

        try:
            return self._value.is_integer()
        except AttributeError:
            pass

        return False

    def is_exclude_instance(self):
        from ..type._realnumber import RealNumber

        return (
            super().is_exclude_instance()
            or isinstance(self._value, bool)
            or RealNumber(self._value, strict_level=1).is_type()
            or (isinstance(self._value, str) and RE_SCIENTIFIC_NOTATION.search(self._value))
        )


class IntegerTypeCheckerStrictLevel2(IntegerTypeCheckerStrictLevel1):
    def is_exclude_instance(self):
        return isinstance(self._value, (str,) + (bool, float, Decimal))


_factory = CheckerFactory(
    checker_mapping={
        0: IntegerTypeCheckerStrictLevel0,
        1: IntegerTypeCheckerStrictLevel1,
        2: IntegerTypeCheckerStrictLevel2,
    }
)


class IntegerTypeChecker(TypeCheckerDelegator):
    def __init__(self, value, strict_level):
        super().__init__(value=value, checker_factory=_factory, strict_level=strict_level)
