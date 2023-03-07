"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import enum
import platform
import re
import string
import warnings
from pathlib import Path
from typing import Any, List, Optional, Union, cast


_re_whitespaces = re.compile(r"^[\s]+$")


@enum.unique
class Platform(enum.Enum):
    POSIX = "POSIX"
    UNIVERSAL = "universal"

    LINUX = "Linux"
    WINDOWS = "Windows"
    MACOS = "macOS"


PathType = Union[str, Path]
PlatformType = Union[str, Platform, None]


def is_pathlike_obj(value: PathType) -> bool:
    return isinstance(value, Path)


def validate_pathtype(
    text: PathType, allow_whitespaces: bool = False, error_msg: Optional[str] = None
) -> None:
    from .error import ErrorReason, ValidationError

    if _is_not_null_string(text) or is_pathlike_obj(text):
        return

    if allow_whitespaces and _re_whitespaces.search(str(text)):
        return

    if is_null_string(text):
        if not error_msg:
            error_msg = "the value must be a not empty"

        raise ValidationError(
            description=error_msg,
            reason=ErrorReason.NULL_NAME,
        )

    raise TypeError(f"text must be a string: actual={type(text)}")


def validate_null_string(text: PathType, error_msg: Optional[str] = None) -> None:
    warnings.warn("'validate_null_string' has moved to 'validate_pathtype'", DeprecationWarning)

    validate_pathtype(text, False, error_msg)


def preprocess(name: PathType) -> str:
    if is_pathlike_obj(name):
        name = str(name)

    return cast(str, name)


def is_null_string(value: Any) -> bool:
    if value is None:
        return True

    try:
        return len(value.strip()) == 0
    except AttributeError:
        return False


def _is_not_null_string(value: Any) -> bool:
    try:
        return len(value.strip()) > 0
    except AttributeError:
        return False


def _get_unprintable_ascii_chars() -> List[str]:
    return [chr(c) for c in range(128) if chr(c) not in string.printable]


unprintable_ascii_chars = tuple(_get_unprintable_ascii_chars())


def _get_ascii_symbols() -> List[str]:
    symbol_list: List[str] = []

    for i in range(128):
        c = chr(i)

        if c in unprintable_ascii_chars or c in string.digits + string.ascii_letters:
            continue

        symbol_list.append(c)

    return symbol_list


ascii_symbols = tuple(_get_ascii_symbols())

__RE_UNPRINTABLE_CHARS = re.compile(
    "[{}]".format(re.escape("".join(unprintable_ascii_chars))), re.UNICODE
)
__RE_ANSI_ESCAPE = re.compile(
    r"(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])"
)


def replace_unprintable_char(text: str, replacement_text: str = "") -> str:
    try:
        return __RE_UNPRINTABLE_CHARS.sub(replacement_text, text)
    except (TypeError, AttributeError):
        raise TypeError("text must be a string")


def replace_ansi_escape(text: str, replacement_text: str = "") -> str:
    try:
        return __RE_ANSI_ESCAPE.sub(replacement_text, text)
    except (TypeError, AttributeError):
        raise TypeError("text must be a string")


def normalize_platform(name: PlatformType) -> Platform:
    if isinstance(name, Platform):
        return name

    if name:
        name = name.strip().casefold()

    if name == "posix":
        return Platform.POSIX

    if name == "auto":
        name = platform.system().casefold()

    if name in ["linux"]:
        return Platform.LINUX

    if name and name.startswith("win"):
        return Platform.WINDOWS

    if name in ["mac", "macos", "darwin"]:
        return Platform.MACOS

    return Platform.UNIVERSAL


def findall_to_str(match: List[Any]) -> str:
    return ", ".join([repr(text) for text in match])
