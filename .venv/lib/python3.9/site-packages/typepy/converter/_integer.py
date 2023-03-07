"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from decimal import Decimal, InvalidOperation

from .._common import remove_thousand_sep, strip_ansi_escape
from .._const import DefaultValue, ParamKey
from ..error import TypeConversionError
from ._interface import AbstractValueConverter


class IntegerConverter(AbstractValueConverter):
    def force_convert(self):
        try:
            value = remove_thousand_sep(self._value)
        except TypeError:
            value = self._value

        try:
            return int(Decimal(value))
        except (TypeError, OverflowError, ValueError, InvalidOperation):
            pass

        if self._params.get(ParamKey.STRIP_ANSI_ESCAPE, DefaultValue.STRIP_ANSI_ESCAPE):
            try:
                return int(Decimal(strip_ansi_escape(value)))
            except (TypeError, OverflowError, ValueError, InvalidOperation):
                pass

        raise TypeConversionError(f"failed to force_convert to int: type={type(value)}")
