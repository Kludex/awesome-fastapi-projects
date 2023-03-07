"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from typing import Any

from .._typecode import Typecode
from ._base import AbstractType


class Binary(AbstractType):
    """
    |result_matrix_desc|

    :py:attr:`.strict_level`
        |strict_level|
    """

    @property
    def typecode(self) -> Typecode:
        return Typecode.STRING

    def __init__(self, value: Any, strict_level: int = 1, **kwargs) -> None:
        super().__init__(value, strict_level, **kwargs)

    def _create_type_checker(self):
        from ..checker import BytesTypeChecker

        return BytesTypeChecker(self._data, self._strict_level)

    def _create_type_converter(self):
        from ..converter import BytesConverter

        return BytesConverter(self._data, self._params)
