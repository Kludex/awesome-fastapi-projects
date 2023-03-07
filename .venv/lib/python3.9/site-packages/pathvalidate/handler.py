"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


from datetime import datetime
from typing import Callable

from .error import ValidationError


Handler = Callable[[ValidationError], str]


def return_null_string(e: ValidationError) -> str:
    return ""


def return_timestamp(e: ValidationError) -> str:
    return str(datetime.now().timestamp())


def raise_error(e: ValidationError) -> str:
    raise e
