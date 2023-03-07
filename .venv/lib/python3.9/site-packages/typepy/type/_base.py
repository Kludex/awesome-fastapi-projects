"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import abc
from typing import Any, Optional

from .._typecode import Typecode
from ..checker._interface import TypeCheckerInterface
from ..converter import ValueConverterInterface
from ..error import TypeConversionError


class AbstractType(TypeCheckerInterface, ValueConverterInterface):
    __slots__ = (
        "_data",
        "_strict_level",
        "_params",
        "__checker",
        "__converter",
        "__is_type_result",
    )

    @abc.abstractproperty
    def typecode(self) -> Typecode:  # pragma: no cover
        pass

    @abc.abstractmethod
    def _create_type_checker(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def _create_type_converter(self):  # pragma: no cover
        pass

    @property
    def typename(self) -> str:
        return self.typecode.name

    def __init__(self, value: Any, strict_level: int, **kwargs) -> None:
        self._data = value
        self._strict_level = strict_level
        self._params = kwargs

        self.__checker = self._create_type_checker()
        self.__converter = self._create_type_converter()

        self.__is_type_result: Optional[bool] = None

    def __repr__(self) -> str:
        return ", ".join(
            [
                f"value={self._data}",
                f"typename={self.typename}",
                f"strict_level={self._strict_level}",
                f"is_type={self.is_type()}",
                f"try_convert={self.try_convert()}",
            ]
        )

    def is_type(self) -> bool:
        """
        :return:
        :rtype: bool
        """

        if self.__is_type_result is not None:
            return self.__is_type_result

        self.__is_type_result = self.__is_type()

        return self.__is_type_result

    def __is_type(self) -> bool:
        if self.__checker.is_type():
            return True

        if self.__checker.is_exclude_instance():
            return False

        try:
            self._converted_value = self.__converter.force_convert()
        except TypeConversionError:
            return False

        if not self.__checker.is_valid_after_convert(self._converted_value):
            return False

        return True

    def validate(self, error_message: Optional[str] = None) -> None:
        """
        :raises TypeError:
            If the value is not matched the type that the class represented.
        """

        if self.is_type():
            return

        if not error_message:
            error_message = "invalid value type"

        raise TypeError(f"{error_message}: expected={self.typename}, actual={type(self._data)}")

    def convert(self):
        """
        :return: Converted value.
        :raises typepy.TypeConversionError:
            If the value cannot convert.
        """

        if self.is_type():
            return self.force_convert()

        raise TypeConversionError(
            "failed to convert {} from {} to {}".format(
                self._data, type(self._data).__name__, self.typename
            )
        )

    def force_convert(self):
        """
        :return: Converted value.
        :raises typepy.TypeConversionError:
            If the value cannot convert.
        """

        return self.__converter.force_convert()

    def try_convert(self):
        """
        :return: Converted value. |None| if failed to convert.
        """

        try:
            return self.convert()
        except TypeConversionError:
            return None
