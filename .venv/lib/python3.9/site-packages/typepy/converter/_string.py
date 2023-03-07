"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from mbstrdecoder import MultiByteStrDecoder

from ._interface import AbstractValueConverter


class StringConverter(AbstractValueConverter):
    def force_convert(self):
        try:
            return MultiByteStrDecoder(self._value).unicode_str
        except ValueError:
            return str(self._value)


class NullStringConverter(StringConverter):
    def force_convert(self):
        return super().force_convert()
