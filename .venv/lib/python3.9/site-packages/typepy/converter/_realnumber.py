"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import decimal

from .._common import strip_ansi_escape
from .._const import DefaultValue, ParamKey
from ..error import TypeConversionError
from ._interface import AbstractValueConverter


class FloatConverter(AbstractValueConverter):
    def __init__(self, value, params):
        super().__init__(value, params)

        self.float_class = self._params.get("float_type")
        if self.float_class is None:
            self.float_class = DefaultValue.FLOAT_TYPE

    def force_convert(self):
        if isinstance(self._value, self.float_class):
            return self._value

        if isinstance(self._value, float):
            return self.float_class(str(self._value))

        try:
            return self.float_class(self._value)
        except (TypeError, ValueError, decimal.InvalidOperation):
            pass

        if self._params.get(ParamKey.STRIP_ANSI_ESCAPE, DefaultValue.STRIP_ANSI_ESCAPE):
            try:
                return self.float_class(strip_ansi_escape(self._value))
            except (TypeError, ValueError, decimal.InvalidOperation):
                pass

        raise TypeConversionError(f"failed to force_convert to float: type={type(self._value)}")
