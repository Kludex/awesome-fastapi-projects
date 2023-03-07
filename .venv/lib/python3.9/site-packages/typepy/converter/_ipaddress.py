"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from .._common import strip_ansi_escape
from .._const import DefaultValue, ParamKey
from ..error import TypeConversionError
from ._interface import AbstractValueConverter


class IpAddressConverter(AbstractValueConverter):
    def force_convert(self):
        import ipaddress

        value = str(self._value)

        try:
            return ipaddress.ip_address(value)
        except ValueError:
            pass

        if self._params.get(ParamKey.STRIP_ANSI_ESCAPE, DefaultValue.STRIP_ANSI_ESCAPE):
            try:
                return ipaddress.ip_address(strip_ansi_escape(value))
            except ValueError:
                pass

        raise TypeConversionError(
            f"failed to force_convert to dictionary: type={type(self._value)}"
        )
