"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from typing import Any

from .._typecode import Typecode
from ..checker import DateTimeTypeChecker
from ..converter import DateTimeConverter
from ._base import AbstractType


class DateTime(AbstractType):
    """
    |result_matrix_desc|

    .. include:: matrix_datetime_type.txt

    :py:attr:`.strict_level`
        |strict_level|
    """

    @property
    def typecode(self) -> Typecode:
        return Typecode.DATETIME

    def __init__(self, value: Any, strict_level: int = 2, **kwargs) -> None:
        super().__init__(value, strict_level, **kwargs)

    def _create_type_checker(self):
        return DateTimeTypeChecker(self._data, self._strict_level)

    def _create_type_converter(self):
        return DateTimeConverter(self._data, self._params)
