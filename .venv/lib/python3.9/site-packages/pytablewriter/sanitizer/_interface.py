"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import abc
from typing import List

from pathvalidate import validate_pathtype


class NameSanitizer(metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def reserved_keywords(self) -> List:  # pragma: no cover
        pass

    @abc.abstractmethod
    def validate(self) -> None:  # pragma: no cover
        pass

    @abc.abstractmethod
    def sanitize(self, replacement_text: str = "") -> str:  # pragma: no cover
        pass

    @property
    def _str(self) -> str:
        return str(self._value)

    def __init__(self, value: str) -> None:
        self._validate_null_string(value)

        self._value = value.strip()

    def _is_reserved_keyword(self, value: str) -> bool:
        return value in self.reserved_keywords

    @staticmethod
    def _validate_null_string(text: str) -> None:
        validate_pathtype(text, error_msg="null name")
