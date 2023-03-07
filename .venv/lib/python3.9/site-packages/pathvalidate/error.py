"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import enum
from typing import Optional, cast

from ._common import Platform


@enum.unique
class ErrorReason(enum.Enum):
    """
    Validation error reasons.
    """

    FOUND_ABS_PATH = "FOUND_ABS_PATH"  #: found an absolute path when expecting a file name
    NULL_NAME = "NULL_NAME"  #: empty value
    INVALID_CHARACTER = "INVALID_CHARACTER"  #: found invalid characters(s) in a value
    INVALID_LENGTH = "INVALID_LENGTH"  #: found invalid string length
    MALFORMED_ABS_PATH = "MALFORMED_ABS_PATH"  #: found invalid absolute path format
    RESERVED_NAME = "RESERVED_NAME"  #: found a reserved name by a platform


class ValidationError(ValueError):
    """
    Exception class of validation errors.

    .. py:attribute:: reason

        The cause of the error.

        Returns:
            :py:class:`~pathvalidate.error.ErrorReason`:
    """

    @property
    def platform(self) -> Platform:
        return self.__platform

    @property
    def reason(self) -> Optional[ErrorReason]:
        return self.__reason

    @property
    def description(self) -> str:
        return self.__description

    @property
    def reserved_name(self) -> str:
        return self.__reserved_name

    @property
    def reusable_name(self) -> bool:
        return self.__reusable_name

    def __init__(self, *args, **kwargs):
        self.__platform = kwargs.pop("platform", None)
        self.__reason = kwargs.pop("reason", None)
        self.__description = kwargs.pop("description", None)
        self.__reserved_name = kwargs.pop("reserved_name", None)
        self.__reusable_name = kwargs.pop("reusable_name", None)

        try:
            super().__init__(*args[0], **kwargs)
        except IndexError:
            super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        item_list = []

        if Exception.__str__(self):
            item_list.append(Exception.__str__(self))

        if self.reason:
            item_list.append(f"reason={cast(ErrorReason, self.reason).value}")
        if self.platform:
            item_list.append(f"target-platform={self.platform.value}")
        if self.description:
            item_list.append(f"description={self.description}")
        if self.__reusable_name is not None:
            item_list.append(f"reusable_name={self.reusable_name}")

        return ", ".join(item_list).strip()

    def __repr__(self, *args, **kwargs):
        return self.__str__(*args, **kwargs)


class NullNameError(ValidationError):
    """
    Exception raised when a name is empty.
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs["reason"] = ErrorReason.NULL_NAME

        super().__init__(args, **kwargs)


class InvalidCharError(ValidationError):
    """
    Exception raised when includes invalid character(s) within a string.
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs["reason"] = ErrorReason.INVALID_CHARACTER

        super().__init__(args, **kwargs)


class InvalidLengthError(ValidationError):
    """
    Exception raised when a string too long/short.
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs["reason"] = ErrorReason.INVALID_LENGTH

        super().__init__(args, **kwargs)


class ReservedNameError(ValidationError):
    """
    Exception raised when a string matched a reserved name.
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs["reason"] = ErrorReason.RESERVED_NAME

        super().__init__(args, **kwargs)


class ValidReservedNameError(ReservedNameError):
    """
    Exception raised when a string matched a reserved name.
    However, it can be used as a name.
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs["reusable_name"] = True

        super().__init__(args, **kwargs)


class InvalidReservedNameError(ReservedNameError):
    """
    Exception raised when a string matched a reserved name.
    Moreover, the reserved name is invalid as a name.
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs["reusable_name"] = False

        super().__init__(args, **kwargs)
