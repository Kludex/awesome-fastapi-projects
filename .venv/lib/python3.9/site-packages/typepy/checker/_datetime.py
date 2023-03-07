"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from datetime import date, datetime

from ._checker import CheckerFactory, TypeCheckerBase, TypeCheckerDelegator
from ._common import isstring


class DateTimeTypeCheckerStrictLevel0(TypeCheckerBase):
    def is_instance(self):
        return isinstance(self._value, (date, datetime))


class DateTimeTypeCheckerStrictLevel1(DateTimeTypeCheckerStrictLevel0):
    def is_exclude_instance(self):
        from ..type._integer import Integer

        # exclude timestamp
        return Integer(self._value, strict_level=1).is_type()


class DateTimeTypeCheckerStrictLevel2(DateTimeTypeCheckerStrictLevel1):
    def is_exclude_instance(self):
        return isstring(self._value) or super().is_exclude_instance()


_factory = CheckerFactory(
    checker_mapping={
        0: DateTimeTypeCheckerStrictLevel0,
        1: DateTimeTypeCheckerStrictLevel1,
        2: DateTimeTypeCheckerStrictLevel2,
    }
)


class DateTimeTypeChecker(TypeCheckerDelegator):
    def __init__(self, value, strict_level):
        super().__init__(value=value, checker_factory=_factory, strict_level=strict_level)
