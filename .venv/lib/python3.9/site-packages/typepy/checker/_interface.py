"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import abc


class TypeCheckerInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def is_type(self) -> bool:  # pragma: no cover
        pass

    @abc.abstractmethod
    def validate(self) -> None:  # pragma: no cover
        pass
