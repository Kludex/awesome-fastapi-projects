"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from ._checker import CheckerFactory, TypeCheckerBase, TypeCheckerDelegator


class DictionaryTypeCheckerStrictLevel0(TypeCheckerBase):
    def is_instance(self):
        return isinstance(self._value, dict)

    def is_valid_after_convert(self, converted_value):
        return isinstance(converted_value, dict) and converted_value


class DictionaryTypeCheckerStrictLevel1(DictionaryTypeCheckerStrictLevel0):
    def is_exclude_instance(self):
        return not isinstance(self._value, dict)


_factory = CheckerFactory(
    checker_mapping={0: DictionaryTypeCheckerStrictLevel0, 1: DictionaryTypeCheckerStrictLevel1}
)


class DictionaryTypeChecker(TypeCheckerDelegator):
    def __init__(self, value, strict_level):
        super().__init__(value=value, checker_factory=_factory, strict_level=strict_level)
