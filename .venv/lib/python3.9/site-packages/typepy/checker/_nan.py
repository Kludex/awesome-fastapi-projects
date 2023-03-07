"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from ._checker import CheckerFactory, TypeCheckerBase, TypeCheckerDelegator
from ._common import isnan, isstring


class NanTypeCheckerStrictLevel0(TypeCheckerBase):
    def is_instance(self):
        return isnan(self._value)

    def is_valid_after_convert(self, converted_value):
        return isnan(converted_value)


class NanTypeCheckerStrictLevel1(NanTypeCheckerStrictLevel0):
    def is_exclude_instance(self):
        return isstring(self._value)


_factory = CheckerFactory(
    checker_mapping={0: NanTypeCheckerStrictLevel0, 1: NanTypeCheckerStrictLevel1}
)


class NanTypeChecker(TypeCheckerDelegator):
    def __init__(self, value, strict_level):
        super().__init__(value=value, checker_factory=_factory, strict_level=strict_level)
