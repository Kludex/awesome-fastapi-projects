"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from ._checker import CheckerFactory, TypeCheckerBase, TypeCheckerDelegator


class NoneTypeCheckerStrictLevel0(TypeCheckerBase):
    def is_instance(self):
        return self._value is None

    def is_valid_after_convert(self, converted_value):
        return self._value is None


_factory = CheckerFactory(checker_mapping={0: NoneTypeCheckerStrictLevel0})


class NoneTypeChecker(TypeCheckerDelegator):
    def __init__(self, value, strict_level):
        super().__init__(value=value, checker_factory=_factory, strict_level=strict_level)
