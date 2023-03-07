"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from ._checker import CheckerFactory, TypeCheckerBase, TypeCheckerDelegator


class BytesTypeCheckerStrictLevel0(TypeCheckerBase):
    def is_instance(self):
        return isinstance(self._value, bytes)

    def is_valid_after_convert(self, converted_value):
        return isinstance(converted_value, bytes)


_factory = CheckerFactory(checker_mapping={0: BytesTypeCheckerStrictLevel0})


class BytesTypeChecker(TypeCheckerDelegator):
    def __init__(self, value, strict_level):
        super().__init__(value=value, checker_factory=_factory, strict_level=strict_level)
