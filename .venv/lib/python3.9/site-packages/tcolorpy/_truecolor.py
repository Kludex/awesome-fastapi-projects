import re
from collections import namedtuple
from colorsys import rgb_to_hsv
from enum import Enum
from typing import List, Optional, Sequence, Tuple, Type, Union, cast  # noqa

from ._const import CSI, RESET, AnsiBGColor, AnsiFGColor, AnsiStyle


RGBTuple = Tuple[int, int, int]

HSV = namedtuple("HSV", "hue saturation value")

_regexp_color_code = re.compile(
    "^#?(?P<red>[0-9a-f]{2})(?P<green>[0-9a-f]{2})(?P<blue>[0-9a-f]{2})$", re.IGNORECASE
)
_regexp_normalize = re.compile(r"[\s_-]")
name_to_rgb = {
    "BLACK": (0, 0, 0),
    "RED": (205, 49, 49),
    "GREEN": (13, 188, 121),
    "YELLOW": (229, 229, 16),
    "BLUE": (36, 114, 200),
    "MAGENTA": (188, 63, 188),
    "CYAN": (17, 168, 205),
    "WHITE": (229, 229, 229),
    "LIGHTBLACK": (102, 102, 102),
    "LIGHTRED": (241, 76, 76),
    "LIGHTGREEN": (35, 209, 139),
    "LIGHTYELLOW": (245, 245, 67),
    "LIGHTBLUE": (59, 142, 234),
    "LIGHTMAGENTA": (214, 112, 214),
    "LIGHTCYAN": (41, 184, 219),
    "LIGHTWHITE": (255, 255, 255),
}


def _normalize_name(name: str) -> str:
    return _regexp_normalize.sub("", name).upper()


class Color:
    def __init__(self, color: Union["Color", str, RGBTuple]) -> None:
        self.__name = ""
        self.__is_color_code_src = False
        self.__hsv: Optional[HSV] = None

        if color is None:
            raise TypeError("color must be one of Color/str/RGBTuple")

        if isinstance(color, str):
            color = _normalize_name(color)
            try:
                self.__from_color_name(color)
            except KeyError:
                self.__from_color_code(color)

            return

        try:
            # from a RGBTuple instance
            self.red, self.green, self.blue = color  # type: ignore
            self.__validate_rgb_value(self.red)
            self.__validate_rgb_value(self.green)
            self.__validate_rgb_value(self.blue)
        except TypeError:
            # from a Color instance
            self.__name = color.name  # type: ignore
            self.red, self.green, self.blue = color.red, color.green, color.blue  # type: ignore

    def __eq__(self, other) -> bool:
        if self.name and other.name:
            return self.name == other.name
        elif self.name or other.name:
            return False

        if all([self.red == other.red, self.green == other.green, self.blue == other.blue]):
            return True

        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        items = [f"code={self.color_code}, rgb=({self.red}, {self.green}, {self.blue})"]

        if self.__name:
            items.append(f"name={self.__name}")

        return "Color({})".format(", ".join(items))

    def __from_color_code(self, color_code: str) -> None:
        match = _regexp_color_code.search(color_code)
        if match is None:
            raise ValueError(f"invalid color code found: {color_code}")

        self.__is_color_code_src = True
        red, green, blue = match.group(1, 2, 3)
        self.red = int(red, 16)
        self.green = int(green, 16)
        self.blue = int(blue, 16)

    def __from_color_name(self, name: str) -> None:
        self.red, self.green, self.blue = name_to_rgb[name]
        self.__name = name

    def __validate_rgb_value(self, n: int) -> None:
        if not (0 <= n <= 255):
            raise ValueError("value must be within 0-255")

    @property
    def name(self) -> str:
        return self.__name

    @property
    def is_color_code_src(self) -> bool:
        return self.__is_color_code_src

    @property
    def color_code(self) -> str:
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"

    @property
    def hsv(self) -> HSV:
        if self.__hsv is None:
            self.__hsv = HSV(*rgb_to_hsv(self.red / 255, self.green / 255, self.blue / 255))

        return self.__hsv

    def calc_scaler(self) -> int:
        return self.red + self.green + self.blue

    def calc_complementary(self):
        rgb = (self.red, self.green, self.blue)
        n = max(rgb) + min(rgb)
        return Color((n - self.red, n - self.green, n - self.blue))


def _normalize_enum(value, enum_class: Type[Enum]):
    if isinstance(value, enum_class):
        return value

    try:
        return enum_class[_normalize_name(value)]
    except AttributeError:
        raise TypeError(f"value must be a {enum_class} or a str: actual={type(value)}")
    except KeyError:
        raise ValueError(
            "invalid value found: expected={}, actual={}".format(
                "/".join([item.name for item in enum_class]), value
            )
        )


def _ansi_escape(value: str) -> str:
    return f"{CSI}{value}m"


def _to_ansi_style(style: Union[str, AnsiStyle]) -> str:
    return _ansi_escape(f"{_normalize_enum(style, AnsiStyle).value}")


def _to_ansi_fg_truecolor(color: Color) -> str:
    return _ansi_escape(f"38;2;{color.red};{color.green};{color.blue}")


def _to_ansi_bg_truecolor(color: Color) -> str:
    return _ansi_escape(f"48;2;{color.red};{color.green};{color.blue}")


def _to_ansi_fg_color(color: AnsiFGColor) -> str:
    return _ansi_escape(f"{color.value}")


def _to_ansi_bg_color(color: AnsiBGColor) -> str:
    return _ansi_escape(f"{color.value}")


def _make_ansi_fg_truecolor(color: Union[Color, str, RGBTuple, AnsiFGColor, None]) -> str:
    if isinstance(color, AnsiFGColor):
        return _to_ansi_fg_color(color)

    if isinstance(color, Color):
        if color.name:
            return _to_ansi_fg_color(_normalize_enum(color.name, AnsiFGColor))

        return _to_ansi_fg_truecolor(color)

    if isinstance(color, str):
        try:
            return _to_ansi_fg_color(_normalize_enum(color, AnsiFGColor))
        except ValueError:
            c = Color(color)
    elif isinstance(color, (tuple, list)):
        c = Color(color)
    else:
        c = color  # type: ignore

    return _to_ansi_fg_truecolor(c) if c else ""


def _make_ansi_bg_truecolor(color: Union[Color, str, RGBTuple, AnsiBGColor, None]) -> str:
    if isinstance(color, AnsiBGColor):
        return _to_ansi_bg_color(color)

    if isinstance(color, Color):
        if color.name:
            return _to_ansi_bg_color(_normalize_enum(color.name, AnsiBGColor))

        return _to_ansi_bg_truecolor(color)

    if isinstance(color, str):
        try:
            return _to_ansi_bg_color(_normalize_enum(color, AnsiBGColor))
        except ValueError:
            c = Color(color)
    elif isinstance(color, (tuple, list)):
        c = Color(color)
    else:
        c = color  # type: ignore

    return _to_ansi_bg_truecolor(c) if c else ""


def tcolor(
    string: str,
    color: Union[Color, str, RGBTuple, AnsiFGColor, None] = None,
    bg_color: Union[Color, str, RGBTuple, AnsiBGColor, None] = None,
    styles: Optional[Sequence[Union[str, AnsiStyle]]] = None,
) -> str:
    ansi_fg_color = _make_ansi_fg_truecolor(color)
    ansi_bg_color = _make_ansi_bg_truecolor(bg_color)

    ansi_styles: List[str] = []
    if styles:
        ansi_styles = [_to_ansi_style(style) for style in styles]

    reset = RESET
    if not ansi_fg_color and not ansi_bg_color and not ansi_styles:
        reset = ""

    return "".join(ansi_styles + [ansi_bg_color, ansi_fg_color, string, reset])
