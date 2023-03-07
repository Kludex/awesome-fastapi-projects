"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import warnings

import click

from ._common import PathType
from ._filename import sanitize_filename, validate_filename
from ._filepath import sanitize_filepath, validate_filepath
from .error import ValidationError


def validate_filename_arg(ctx, param, value) -> str:
    if not value:
        return ""

    try:
        validate_filename(value)
    except ValidationError as e:
        raise click.BadParameter(str(e))

    return value


def validate_filepath_arg(ctx, param, value) -> str:
    if not value:
        return ""

    try:
        validate_filepath(value)
    except ValidationError as e:
        raise click.BadParameter(str(e))

    return value


def sanitize_filename_arg(ctx, param, value) -> PathType:
    if not value:
        return ""

    return sanitize_filename(value)


def sanitize_filepath_arg(ctx, param, value) -> PathType:
    if not value:
        return ""

    return sanitize_filepath(value)


def filename(ctx, param, value):  # pragma: no cover
    warnings.warn("'filename' has moved to 'validate_filename'", DeprecationWarning)

    if not value:
        return None

    try:
        validate_filename(value)
    except ValidationError as e:
        raise click.BadParameter(str(e))

    return sanitize_filename(value)


def filepath(ctx, param, value):  # pragma: no cover
    warnings.warn("'filepath' has moved to 'validate_filepath'", DeprecationWarning)

    if not value:
        return None

    try:
        validate_filepath(value)
    except ValidationError as e:
        raise click.BadParameter(str(e))

    return sanitize_filepath(value)
