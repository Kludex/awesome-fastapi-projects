"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from ..error import TypeConversionError
from ._interface import AbstractValueConverter


class BytesConverter(AbstractValueConverter):
    def force_convert(self):
        raise TypeConversionError("not inmplemented")
