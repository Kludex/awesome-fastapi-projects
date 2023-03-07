"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import abc

from ..error import TypeConversionError


class ValueConverterInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def force_convert(self):  # pragma: no cover
        pass


class AbstractValueConverter(ValueConverterInterface):
    __slots__ = "_value"

    def __init__(self, value, params):
        self._value = value
        self._params = params

    def __repr__(self):
        try:
            string = str(self.force_convert())
        except TypeConversionError:
            string = "[ValueConverter ERROR] failed to force_convert"

        return string
