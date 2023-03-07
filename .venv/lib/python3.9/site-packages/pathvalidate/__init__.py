"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from .__version__ import __author__, __copyright__, __email__, __license__, __version__
from ._base import AbstractSanitizer, AbstractValidator
from ._common import (
    Platform,
    ascii_symbols,
    normalize_platform,
    replace_ansi_escape,
    replace_unprintable_char,
    unprintable_ascii_chars,
    validate_null_string,
    validate_pathtype,
)
from ._filename import FileNameSanitizer, is_valid_filename, sanitize_filename, validate_filename
from ._filepath import (
    FilePathSanitizer,
    is_valid_filepath,
    sanitize_file_path,
    sanitize_filepath,
    validate_file_path,
    validate_filepath,
)
from ._ltsv import sanitize_ltsv_label, validate_ltsv_label
from ._symbol import replace_symbol, validate_symbol
from .error import (
    ErrorReason,
    InvalidCharError,
    InvalidLengthError,
    InvalidReservedNameError,
    NullNameError,
    ReservedNameError,
    ValidationError,
    ValidReservedNameError,
)


__all__ = (
    "__author__",
    "__copyright__",
    "__email__",
    "__license__",
    "__version__",
    "AbstractSanitizer",
    "AbstractValidator",
    "Platform",
    "ascii_symbols",
    "normalize_platform",
    "replace_ansi_escape",
    "replace_unprintable_char",
    "unprintable_ascii_chars",
    "validate_pathtype",
    "FileNameSanitizer",
    "is_valid_filename",
    "sanitize_filename",
    "validate_filename",
    "FilePathSanitizer",
    "is_valid_filepath",
    "sanitize_filepath",
    "validate_filepath",
    "sanitize_ltsv_label",
    "validate_ltsv_label",
    "replace_symbol",
    "validate_symbol",
    "ErrorReason",
    "InvalidCharError",
    "InvalidLengthError",
    "InvalidReservedNameError",
    "NullNameError",
    "ReservedNameError",
    "ValidationError",
    "ValidReservedNameError",
)
