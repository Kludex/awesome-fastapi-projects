"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from typing import Any

from .._typecode import Typecode
from ..checker import DictionaryTypeChecker
from ..converter import DictionaryConverter
from ._base import AbstractType


class Dictionary(AbstractType):
    """
    |result_matrix_desc|

    .. include:: matrix_dictionary_type.txt

    :py:attr:`.strict_level`
        |strict_level|
    """

    @property
    def typecode(self) -> Typecode:
        return Typecode.DICTIONARY

    def __init__(self, value: Any, strict_level: int = 1, **kwargs) -> None:
        super().__init__(value, strict_level, **kwargs)

    def _create_type_checker(self):
        return DictionaryTypeChecker(self._data, self._strict_level)

    def _create_type_converter(self):
        return DictionaryConverter(self._data, self._params)
