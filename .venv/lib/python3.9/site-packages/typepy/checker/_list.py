"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from ._checker import CheckerFactory, TypeCheckerBase, TypeCheckerDelegator
from ._common import isstring


class ListTypeCheckerStrictLevel0(TypeCheckerBase):
    def is_instance(self):
        return isinstance(self._value, list)

    def is_valid_after_convert(self, converted_value):
        return isinstance(converted_value, list) and converted_value

    def is_exclude_instance(self):
        return isstring(self._value)


class ListTypeCheckerStrictLevel1(ListTypeCheckerStrictLevel0):
    def is_exclude_instance(self):
        return super().is_exclude_instance() or not isinstance(self._value, list)


_factory = CheckerFactory(
    checker_mapping={0: ListTypeCheckerStrictLevel0, 1: ListTypeCheckerStrictLevel1}
)


class ListTypeChecker(TypeCheckerDelegator):
    def __init__(self, value, strict_level):
        super().__init__(value=value, checker_factory=_factory, strict_level=strict_level)
