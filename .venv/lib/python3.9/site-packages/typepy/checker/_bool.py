"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from .._const import StrictLevel
from ._checker import CheckerFactory, TypeCheckerBase, TypeCheckerDelegator
from ._common import isstring


class BoolTypeCheckerStrictLevel0(TypeCheckerBase):
    def is_instance(self):
        return isinstance(self._value, bool)

    def is_valid_after_convert(self, converted_value):
        return isinstance(converted_value, bool)


class BoolTypeCheckerStrictLevel1(BoolTypeCheckerStrictLevel0):
    def is_exclude_instance(self):
        from ..type._integer import Integer

        return Integer(self._value, strict_level=StrictLevel.MAX).is_type()


class BoolTypeCheckerStrictLevel2(BoolTypeCheckerStrictLevel1):
    def is_exclude_instance(self):
        return super().is_exclude_instance() or isstring(self._value)


_factory = CheckerFactory(
    checker_mapping={
        0: BoolTypeCheckerStrictLevel0,
        1: BoolTypeCheckerStrictLevel1,
        2: BoolTypeCheckerStrictLevel2,
    }
)


class BoolTypeChecker(TypeCheckerDelegator):
    def __init__(self, value, strict_level):
        super().__init__(value=value, checker_factory=_factory, strict_level=strict_level)
