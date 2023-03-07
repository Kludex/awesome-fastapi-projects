"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from ._interface import AbstractValueConverter


class NopConverter(AbstractValueConverter):
    def force_convert(self):
        return self._value
