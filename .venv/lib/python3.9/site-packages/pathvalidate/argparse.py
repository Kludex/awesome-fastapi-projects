"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import warnings
from argparse import ArgumentTypeError

from ._common import PathType
from ._filename import sanitize_filename, validate_filename
from ._filepath import sanitize_filepath, validate_filepath
from .error import ValidationError


def validate_filename_arg(value: str) -> str:
    if not value:
        return ""

    try:
        validate_filename(value)
    except ValidationError as e:
        raise ArgumentTypeError(e)

    return value


def validate_filepath_arg(value: str) -> str:
    if not value:
        return ""

    try:
        validate_filepath(value, platform="auto")
    except ValidationError as e:
        raise ArgumentTypeError(e)

    return value


def sanitize_filename_arg(value: str) -> PathType:
    if not value:
        return ""

    return sanitize_filename(value)


def sanitize_filepath_arg(value: str) -> PathType:
    if not value:
        return ""

    return sanitize_filepath(value, platform="auto")


def filename(value: PathType) -> PathType:  # pragma: no cover
    warnings.warn("'filename' has moved to 'validate_filename'", DeprecationWarning)

    try:
        validate_filename(value)
    except ValidationError as e:
        raise ArgumentTypeError(e)

    return sanitize_filename(value)


def filepath(value: PathType) -> PathType:  # pragma: no cover
    warnings.warn("'filepath' has moved to 'validate_filepath'", DeprecationWarning)

    try:
        validate_filepath(value)
    except ValidationError as e:
        raise ArgumentTypeError(e)

    return sanitize_filepath(value)
