"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import re

from pathvalidate import validate_pathtype
from pathvalidate.error import ErrorReason, ValidationError

from ._base import _preprocess


__MAX_SHEET_NAME_LEN = 31

__INVALID_EXCEL_CHARS = "[]:*?/\\"

__RE_INVALID_EXCEL_SHEET_NAME = re.compile(f"[{re.escape(__INVALID_EXCEL_CHARS):s}]", re.UNICODE)


def validate_excel_sheet_name(sheet_name: str) -> None:
    """
    :param str sheet_name: Excel sheet name to validate.
    :raises pathvalidate.ValidationError (ErrorReason.INVALID_CHARACTER):
        If the ``sheet_name`` includes invalid char(s):
        |invalid_excel_sheet_chars|.
    :raises pathvalidate.ValidationError (ErrorReason.INVALID_LENGTH):
        If the ``sheet_name`` is longer than 31 characters.
    """

    validate_pathtype(sheet_name)

    if len(sheet_name) > __MAX_SHEET_NAME_LEN:
        raise ValidationError(
            description="sheet name is too long: expected<={:d}, actual={:d}".format(
                __MAX_SHEET_NAME_LEN, len(sheet_name)
            ),
            reason=ErrorReason.INVALID_LENGTH,
        )

    unicode_sheet_name = _preprocess(sheet_name)
    match = __RE_INVALID_EXCEL_SHEET_NAME.search(unicode_sheet_name)
    if match is not None:
        raise ValidationError(
            description="invalid char found in the sheet name: '{:s}'".format(
                re.escape(match.group())
            ),
            reason=ErrorReason.INVALID_CHARACTER,
        )


def sanitize_excel_sheet_name(sheet_name: str, replacement_text: str = "") -> str:
    """
    Replace invalid characters for an Excel sheet name within
    the ``sheet_name`` with the ``replacement_text``.
    Invalid characters are as follows:
    |invalid_excel_sheet_chars|.
    The ``sheet_name`` truncate to 31 characters
    (max sheet name length of Excel) from the head, if the length
    of the name is exceed 31 characters.

    :param str sheet_name: Excel sheet name to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If the ``sheet_name`` is an invalid sheet name.
    """

    try:
        unicode_sheet_name = _preprocess(sheet_name)
    except AttributeError as e:
        raise ValueError(e)

    modify_sheet_name = __RE_INVALID_EXCEL_SHEET_NAME.sub(replacement_text, unicode_sheet_name)

    return modify_sheet_name[:__MAX_SHEET_NAME_LEN]
