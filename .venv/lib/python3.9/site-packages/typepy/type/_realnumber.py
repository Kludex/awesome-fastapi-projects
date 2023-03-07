"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from typing import Any

from .._typecode import Typecode
from ._base import AbstractType


class RealNumber(AbstractType):
    """
    |result_matrix_desc|

    .. include:: matrix_realnumber_type.txt

    :py:attr:`.strict_level`
        |strict_level|
    """

    @property
    def typecode(self) -> Typecode:
        return Typecode.REAL_NUMBER

    def __init__(self, value: Any, strict_level: int = 0, **kwargs) -> None:
        super().__init__(value, strict_level, **kwargs)

    def _create_type_checker(self):
        from ..checker._realnumber import RealNumberTypeChecker

        return RealNumberTypeChecker(self._data, self._strict_level)

    def _create_type_converter(self):
        from ..converter._realnumber import FloatConverter

        converter = FloatConverter(self._data, self._params)

        return converter
