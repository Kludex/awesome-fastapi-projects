"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import abc


class DataPeropertyInterface(metaclass=abc.ABCMeta):
    __slots__ = ()

    @abc.abstractproperty
    def align(self):  # pragma: no cover
        pass

    @abc.abstractproperty
    def decimal_places(self):  # pragma: no cover
        pass

    @abc.abstractproperty
    def typecode(self):  # pragma: no cover
        pass

    @abc.abstractproperty
    def typename(self):  # pragma: no cover
        pass
