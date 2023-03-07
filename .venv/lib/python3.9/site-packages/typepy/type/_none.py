"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from typing import Any

from .._typecode import Typecode
from ..checker import NoneTypeChecker
from ..converter import NopConverter
from ._base import AbstractType


class NoneType(AbstractType):
    """
    |result_matrix_desc|

    .. include:: matrix_none_type.txt

    :py:attr:`.strict_level`
        |strict_level|
    """

    @property
    def typecode(self) -> Typecode:
        return Typecode.NONE

    def __init__(self, value: Any, strict_level: int = 0, **kwargs) -> None:
        super().__init__(value, strict_level, **kwargs)

    def force_convert(self):
        return None

    def _create_type_checker(self):
        return NoneTypeChecker(self._data, self._strict_level)

    def _create_type_converter(self):
        return NopConverter(self._data, self._params)
