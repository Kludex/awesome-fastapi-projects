"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from typing import Any

from .._typecode import Typecode
from ._base import AbstractType


class Integer(AbstractType):
    """
    |result_matrix_desc|

    .. include:: matrix_integer_type.txt

    :py:attr:`.strict_level`
        |strict_level|
    """

    @property
    def typecode(self) -> Typecode:
        return Typecode.INTEGER

    def __init__(self, value: Any, strict_level: int = 1, **kwargs) -> None:
        super().__init__(value, strict_level, **kwargs)

    def _create_type_checker(self):
        from ..checker._integer import IntegerTypeChecker

        return IntegerTypeChecker(self._data, self._strict_level)

    def _create_type_converter(self):
        from ..converter._integer import IntegerConverter

        return IntegerConverter(self._data, self._params)
