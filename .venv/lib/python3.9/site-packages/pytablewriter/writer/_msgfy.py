"""
Import from https://github.com/thombashi/msgfy
"""

import inspect
import os.path
from typing import Optional


DEFAULT_ERROR_MESSAGE_FORMAT = "{exception}: {error_msg}"
DEFAULT_DEBUG_MESSAGE_FORMAT = "{exception} {file_name}({line_no}) {func_name}: {error_msg}"

error_message_format = DEFAULT_ERROR_MESSAGE_FORMAT
debug_message_format = DEFAULT_DEBUG_MESSAGE_FORMAT


def _to_message(exception_obj: Exception, format_str: str, frame) -> str:
    if not isinstance(exception_obj, Exception):
        raise ValueError("exception_obj must be an instance of a subclass of the Exception class")

    try:
        return (
            format_str.replace("{exception}", exception_obj.__class__.__name__)
            .replace("{file_name}", os.path.basename(frame.f_code.co_filename))
            .replace("{line_no}", str(frame.f_lineno))
            .replace("{func_name}", frame.f_code.co_name)
            .replace("{error_msg}", str(exception_obj))
        )
    except AttributeError:
        raise ValueError("format_str must be a string")


def to_error_message(exception_obj: Exception, format_str: Optional[str] = None):
    if not format_str:
        format_str = error_message_format

    frame = inspect.currentframe()
    if frame is None:
        return str(exception_obj)

    return _to_message(exception_obj, format_str, frame.f_back)


def to_debug_message(exception_obj: Exception, format_str: Optional[str] = None):
    if not format_str:
        format_str = debug_message_format

    frame = inspect.currentframe()
    if frame is None:
        return str(exception_obj)

    return _to_message(exception_obj, format_str, frame.f_back)
