"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from typing import Any

from .._typecode import Typecode
from ..checker import NullStringTypeChecker, StringTypeChecker
from ..converter import NullStringConverter, StringConverter
from ._base import AbstractType


class String(AbstractType):
    """
    |result_matrix_desc|

    .. include:: matrix_string_type.txt

    :py:attr:`.strict_level`
        |strict_level|
    """

    @property
    def typecode(self) -> Typecode:
        return Typecode.STRING

    def __init__(self, value: Any, strict_level: int = 1, **kwargs) -> None:
        super().__init__(value, strict_level, **kwargs)

    def _create_type_checker(self) -> StringTypeChecker:
        return StringTypeChecker(self._data, self._strict_level)

    def _create_type_converter(self) -> StringConverter:
        return StringConverter(self._data, self._params)


class NullString(AbstractType):
    """
    |result_matrix_desc|

    .. include:: matrix_nullstring_type.txt

    :py:attr:`.strict_level`
        |strict_level|
    """

    @property
    def typecode(self) -> Typecode:
        return Typecode.NULL_STRING

    def __init__(self, value: Any, strict_level: int = 1, **kwargs) -> None:
        super().__init__(value, strict_level, **kwargs)

    def _create_type_checker(self):
        return NullStringTypeChecker(self._data, self._strict_level)

    def _create_type_converter(self):
        return NullStringConverter(self._data, self._params)
