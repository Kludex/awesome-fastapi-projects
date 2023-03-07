"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from ._checker import CheckerFactory, TypeCheckerBase, TypeCheckerDelegator
from ._common import isstring


class StringTypeCheckerStrictLevel0(TypeCheckerBase):
    def is_instance(self):
        return isstring(self._value)

    def is_valid_after_convert(self, converted_value):
        return isstring(converted_value)

    def _is_null_string(self, value):
        try:
            value = value.strip()
        except AttributeError:
            return False

        return len(value) == 0


class StringTypeCheckerStrictLevel1(StringTypeCheckerStrictLevel0):
    def is_exclude_instance(self):
        return not isstring(self._value)


class StringTypeCheckerStrictLevel2(StringTypeCheckerStrictLevel1):
    def is_exclude_instance(self):
        if super().is_exclude_instance():
            return True

        return self._is_null_string(self._value)


_string_factory = CheckerFactory(
    checker_mapping={
        0: StringTypeCheckerStrictLevel0,
        1: StringTypeCheckerStrictLevel1,
        2: StringTypeCheckerStrictLevel2,
    }
)


class StringTypeChecker(TypeCheckerDelegator):
    def __init__(self, value, strict_level):
        super().__init__(value=value, checker_factory=_string_factory, strict_level=strict_level)


class NullStringTypeCheckerStrictLevel0(StringTypeCheckerStrictLevel0):
    def is_instance(self):
        return self._value is None

    def is_valid_after_convert(self, converted_value):
        return self._is_null_string(converted_value)


class NullStringTypeCheckerStrictLevel1(NullStringTypeCheckerStrictLevel0):
    def is_instance(self):
        return False


_null_string_factory = CheckerFactory(
    checker_mapping={0: NullStringTypeCheckerStrictLevel0, 1: NullStringTypeCheckerStrictLevel1}
)


class NullStringTypeChecker(TypeCheckerDelegator):
    def __init__(self, value, strict_level):
        super().__init__(
            value=value, checker_factory=_null_string_factory, strict_level=strict_level
        )
