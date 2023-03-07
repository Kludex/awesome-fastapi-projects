"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import abc

from ._interface import TypeCheckerInterface


class CheckerFactory:
    __slots__ = ("__min_strict_level", "__max_strict_level", "__checker_mapping")

    @property
    def min_strict_level(self):
        return self.__min_strict_level

    @property
    def max_strict_level(self):
        return self.__max_strict_level

    def __init__(self, checker_mapping):
        self.__checker_mapping = checker_mapping

        self.__min_strict_level = min(checker_mapping)
        self.__max_strict_level = max(checker_mapping)
        self.__checker_mapping[None] = self.__max_strict_level

    def get_checker_class(self, strict_level=None):
        checker_class = self.__checker_mapping.get(strict_level)
        if checker_class:
            return checker_class
        if strict_level < self.min_strict_level:
            return self.__checker_mapping[self.min_strict_level]
        if strict_level > self.max_strict_level:
            return self.__checker_mapping[self.max_strict_level]

        raise ValueError(f"unexpected strict level: {strict_level}")


class TypeCheckerBase(TypeCheckerInterface):
    __slots__ = ("_value",)

    def __init__(self, value):
        self._value = value

    @abc.abstractmethod
    def is_instance(self):
        pass

    def is_type(self) -> bool:
        return self.is_instance() and not self.is_exclude_instance()

    def validate(self) -> None:
        """
        :raises TypeError:
            If the value is not matched the type to be expected.
        """

        if self.is_type():
            return

        raise TypeError(f"invalid value type: actual={type(self._value)}")

    def is_exclude_instance(self):
        return False

    def is_valid_after_convert(self, converted_value):
        return True


class TypeCheckerDelegator(TypeCheckerInterface):
    __slots__ = ("__checker",)

    def __init__(self, value, checker_factory, strict_level):
        self.__checker = checker_factory.get_checker_class(strict_level)(value)

    def is_type(self) -> bool:
        return self.__checker.is_type()

    def is_valid_after_convert(self, value):
        return self.__checker.is_valid_after_convert(value)

    def is_instance(self):
        return self.__checker.is_instance()

    def is_exclude_instance(self):
        return self.__checker.is_exclude_instance()

    def validate(self) -> None:
        self.__checker.validate()
