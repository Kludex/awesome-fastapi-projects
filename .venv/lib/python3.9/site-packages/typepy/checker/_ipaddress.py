"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from ._checker import CheckerFactory, TypeCheckerBase, TypeCheckerDelegator
from ._common import isstring


class IpAddressTypeCheckerStrictLevel0(TypeCheckerBase):
    def is_instance(self):
        return self._is_ipaddress(self._value)

    def is_valid_after_convert(self, converted_value):
        return self._is_ipaddress(converted_value)

    @staticmethod
    def _is_ipaddress(value):
        import ipaddress

        return isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address))


class IpAddressTypeCheckerStrictLevel1(IpAddressTypeCheckerStrictLevel0):
    def is_exclude_instance(self):
        return isstring(self._value) or super().is_exclude_instance()


_factory = CheckerFactory(
    checker_mapping={0: IpAddressTypeCheckerStrictLevel0, 1: IpAddressTypeCheckerStrictLevel1}
)


class IpAddressTypeChecker(TypeCheckerDelegator):
    def __init__(self, value, strict_level):
        super().__init__(value=value, checker_factory=_factory, strict_level=strict_level)
