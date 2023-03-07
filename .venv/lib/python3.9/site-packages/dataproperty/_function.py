"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import decimal
import re
from decimal import Decimal
from typing import Any, Optional, Tuple, Union

from mbstrdecoder import MultiByteStrDecoder
from typepy import Integer, RealNumber, TypeConversionError


decimal.setcontext(decimal.Context(prec=60, rounding=decimal.ROUND_HALF_DOWN))

_ansi_escape = re.compile(r"(\x9b|\x1b\[)[0-?]*[ -\/]*[@-~]", re.IGNORECASE)


def get_integer_digit(value) -> int:
    float_type = RealNumber(value)

    try:
        abs_value = abs(float_type.convert())
    except TypeConversionError:
        try:
            abs_value = abs(Integer(value).convert())
        except TypeConversionError:
            raise ValueError(f"the value must be a number: value='{value}' type='{type(value)}'")

        return len(str(abs_value))

    if abs_value.is_zero():
        return 1

    try:
        return len(str(abs_value.quantize(Decimal("1."), rounding=decimal.ROUND_DOWN)))
    except decimal.InvalidOperation:
        return len(str(abs_value))


class DigitCalculator:
    REGEXP_COMMON_LOG = re.compile(r"[\d\.]+[eE]\-\d+")
    REGEXP_SPLIT = re.compile(r"[eE]\-")

    def get_decimal_places(self, value: Union[str, float, int, Decimal]) -> int:
        if Integer(value).is_type():
            return 0

        float_digit_len = 0
        abs_value = abs(float(value))
        text_value = str(abs_value)
        float_text = "0"
        if text_value.find(".") != -1:
            float_text = text_value.split(".")[1]
            float_digit_len = len(float_text)
        elif self.REGEXP_COMMON_LOG.search(text_value):
            float_text = self.REGEXP_SPLIT.split(text_value)[1]
            float_digit_len = int(float_text)

        return float_digit_len


_digit_calculator = DigitCalculator()


def get_number_of_digit(
    value: Any, max_decimal_places: int = 99
) -> Tuple[Optional[int], Optional[int]]:
    try:
        integer_digits = get_integer_digit(value)
    except (ValueError, TypeError, OverflowError):
        return (None, None)

    try:
        decimal_places: Optional[int] = min(
            _digit_calculator.get_decimal_places(value), max_decimal_places
        )
    except (ValueError, TypeError):
        decimal_places = None

    return (integer_digits, decimal_places)


def is_multibyte_str(text) -> bool:
    from typepy import StrictLevel, String

    if not String(text, strict_level=StrictLevel.MIN).is_type():
        return False

    try:
        unicode_text = MultiByteStrDecoder(text).unicode_str
    except ValueError:
        return False

    try:
        unicode_text.encode("ascii")
    except UnicodeEncodeError:
        return True

    return False


def _validate_eaaw(east_asian_ambiguous_width: int) -> None:
    if east_asian_ambiguous_width in (1, 2):
        return

    raise ValueError(
        "invalid east_asian_ambiguous_width: expected=1 or 2, actual={}".format(
            east_asian_ambiguous_width
        )
    )


def strip_ansi_escape(unicode_str: str) -> str:
    return _ansi_escape.sub("", unicode_str)


def calc_ascii_char_width(unicode_str: str, east_asian_ambiguous_width: int = 1) -> int:
    import unicodedata

    width = 0
    for char in unicode_str:
        char_width = unicodedata.east_asian_width(char)
        if char_width in "WF":
            width += 2
        elif char_width == "A":
            _validate_eaaw(east_asian_ambiguous_width)
            width += east_asian_ambiguous_width
        else:
            width += 1

    return width
