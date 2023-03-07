"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from typing import Any

from .._typecode import Typecode
from ..checker import ListTypeChecker
from ..converter import ListConverter
from ._base import AbstractType


class List(AbstractType):
    """
    |result_matrix_desc|

    .. include:: matrix_list_type.txt

    :py:attr:`.strict_level`
        |strict_level|
    """

    @property
    def typecode(self) -> Typecode:
        return Typecode.LIST

    def __init__(self, value: Any, strict_level: int = 1, **kwargs) -> None:
        super().__init__(value, strict_level, **kwargs)

    def _create_type_checker(self):
        return ListTypeChecker(self._data, self._strict_level)

    def _create_type_converter(self):
        return ListConverter(self._data, self._params)
