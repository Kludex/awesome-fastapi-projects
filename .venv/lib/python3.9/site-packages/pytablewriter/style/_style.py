from enum import Enum, unique
from typing import Optional, Union, cast

from dataproperty import Align
from tcolorpy import Color

from .._function import normalize_enum
from ._font import FontSize, FontStyle, FontWeight


@unique
class DecorationLine(Enum):
    NONE = "none"
    LINE_THROUGH = "line_through"
    STRIKE = "strike"
    UNDERLINE = "underline"


@unique
class ThousandSeparator(Enum):
    NONE = "none"  #: no thousands separator
    COMMA = "comma"  #: ``','`` as thousands separator
    SPACE = "space"  #: ``' '`` as thousands separator
    UNDERSCORE = "underscore"  #: ``'_'`` as thousands separator


@unique
class VerticalAlign(Enum):
    BASELINE = (1 << 0, "baseline")
    TOP = (1 << 1, "top")
    MIDDLE = (1 << 2, "middle")
    BOTTOM = (1 << 3, "bottom")

    @property
    def align_code(self):
        return self.__align_code

    @property
    def align_str(self):
        return self.__align_string

    def __init__(self, code, string):
        self.__align_code = code
        self.__align_string = string


_s_to_ts = {
    "": ThousandSeparator.NONE,
    ",": ThousandSeparator.COMMA,
    " ": ThousandSeparator.SPACE,
    "_": ThousandSeparator.UNDERSCORE,
}


def _normalize_thousand_separator(value: Union[str, ThousandSeparator]) -> ThousandSeparator:
    if isinstance(value, ThousandSeparator):
        return value

    norm_value = _s_to_ts.get(value)
    if norm_value is None:
        return cast(ThousandSeparator, value)

    return norm_value


class Style:
    """Style specifier class for table elements.

    Args:
        color (Union[|str|, tcolorpy.Color, |None|]):
            Text color for cells.
            When using str, specify a color code (``"#XXXXXX"``) or a color name.

            .. note::
                In the current version, only applicable for part of text format writer classes.

        fg_color (Union[|str|, tcolorpy.Color, |None|]):
            Alias to :py:attr:`~.color`.

        bg_color (Union[|str|, tcolorpy.Color, |None|]):
            Background color for cells.
            When using str, specify a color code (``"#XXXXXX"``) or a color name.

            .. note::
                In the current version, only applicable for part of text format writer classes.

        align (|str| / :py:class:`~.style.Align`):
            Horizontal text alignment for cells.
            This can be only applied for text format writer classes.
            Possible string values are:

            - ``"auto"`` (default)
                - Detect data type for each column and set alignment that appropriate
                  for the type automatically
            - ``"left"``
            - ``"right"``
            - ``"center"``

        vertical_align (|str| / :py:class:`~.style.VerticalAlign`):
            Vertical text alignment for cells.
            This can be only applied for HtmlTableWriter class.
            Possible string values are:

            - ``"baseline"`` (default)
            - ``"top"``
            - ``"middle"``
            - ``"bottom"``

        font_size (|str| / :py:class:`~.style.FontSize`):
            Font size specification for cells in a column.
            This can be only applied for HTML/Latex writer classes.
            Possible string values are:

            - ``"tiny"``
            - ``"small"``
            - ``"medium"``
            - ``"large"``
            - ``"none"`` (default: no font size specification)

        font_weight (|str| / :py:class:`~.style.FontWeight`):
            Font weight specification for cells in a column.
            This can be only applied for HTML/Latex/Markdown writer classes.
            Possible string values are:

            - ``"normal"`` (default)
            - ``"bold"``

        font_style (|str| / :py:class:`~.style.FontStyle`):
            Font style specification for cells in a column.
            This can be applied only for HTML/Latex/Markdown writer classes.
            Possible string values are:

            - ``"normal"`` (default)
            - ``"italic"``

        decoration_line (|str| / :py:class:`~.style.DecorationLine`)

            Experiental.
            Possible string values are:

            - ``"line-through"``
            - ``"strike"`` (alias for ``"line-through"``)
            - ``"underline"``
            - ``"none"`` (default)

        thousand_separator (|str| / :py:class:`~.style.ThousandSeparator`):
            Thousand separator specification for numbers in a column.
            This can be only applied for text format writer classes.
            Possible string values are:

            - ``","``/``"comma"``
            - ``" "``/``"space"``
            - ``"_"``/``"underscore"``
            - ``""``/``"none"`` (default)

    Example:
        :ref:`example-style`
    """

    @property
    def align(self) -> Align:
        return self.__align

    @align.setter
    def align(self, value: Align) -> None:
        self.__align = value

    @property
    def vertical_align(self) -> VerticalAlign:
        return self.__valign

    @property
    def decoration_line(self) -> DecorationLine:
        return self.__decoration_line

    @property
    def font_size(self) -> FontSize:
        return self.__font_size

    @property
    def font_style(self) -> FontStyle:
        return self.__font_style

    @property
    def font_weight(self) -> FontWeight:
        return self.__font_weight

    @property
    def color(self) -> Optional[Color]:
        return self.__fg_color

    @property
    def fg_color(self) -> Optional[Color]:
        return self.__fg_color

    @property
    def bg_color(self) -> Optional[Color]:
        return self.__bg_color

    @property
    def thousand_separator(self) -> ThousandSeparator:
        return self.__thousand_separator

    @property
    def padding(self):
        return self.__padding

    @padding.setter
    def padding(self, value: Optional[int]):
        self.__padding = value

    def __init__(self, **kwargs) -> None:
        self.__update_color(initialize=True, **kwargs)
        self.__update_align(initialize=True, **kwargs)
        self.__update_font(initialize=True, **kwargs)
        self.__update_misc(initialize=True, **kwargs)

    def __repr__(self) -> str:
        items = []

        if self.align:
            items.append(f"align={self.align.align_string}")
        if self.padding is not None:
            items.append(f"padding={self.padding}")
        if self.vertical_align:
            items.append(f"valign={self.vertical_align.align_str}")
        if self.color:
            items.append(f"color={self.color}")
        if self.bg_color:
            items.append(f"bg_color={self.bg_color}")
        if self.decoration_line is not DecorationLine.NONE:
            items.append(f"decoration_line={self.decoration_line.value}")
        if self.font_size is not FontSize.NONE:
            items.append(f"font_size={self.font_size.value}")
        if self.font_style:
            items.append(f"font_style={self.font_style.value}")
        if self.font_weight:
            items.append(f"font_weight={self.font_weight.value}")
        if self.thousand_separator is not ThousandSeparator.NONE:
            items.append(f"thousand_separator={self.thousand_separator.value}")

        return "({})".format(", ".join(items))

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return NotImplemented

        return all(
            [
                self.align == other.align,
                self.font_size == other.font_size,
                self.font_style == other.font_style,
                self.font_weight == other.font_weight,
                self.thousand_separator == other.thousand_separator,
            ]
        )

    def __ne__(self, other):
        equal = self.__eq__(other)
        return NotImplemented if equal is NotImplemented else not equal

    def update(self, **kwargs) -> None:
        """Update specified style attributes."""
        self.__update_color(initialize=False, **kwargs)
        self.__update_align(initialize=False, **kwargs)
        self.__update_font(initialize=False, **kwargs)
        self.__update_misc(initialize=False, **kwargs)

    def __update_color(self, initialize: bool, **kwargs) -> None:
        fg_color = kwargs.get("color") or kwargs.get("fg_color")
        if fg_color:
            self.__fg_color: Optional[Color] = Color(fg_color)
        elif initialize:
            self.__fg_color = None

        bg_color = kwargs.get("bg_color")
        if bg_color:
            self.__bg_color: Optional[Color] = Color(bg_color)
        elif initialize:
            self.__bg_color = None

    def __update_font(self, initialize: bool, **kwargs) -> None:
        font_size = kwargs.get("font_size")
        if font_size:
            self.__font_size = normalize_enum(
                kwargs.get("font_size"), FontSize, validate=False, default=FontSize.NONE
            )
        elif initialize:
            self.__font_size = FontSize.NONE
        self.__validate_attr("font_size", (FontSize, str))

        font_style = kwargs.get("font_style")
        if font_style:
            self.__font_style = normalize_enum(font_style, FontStyle, default=FontStyle.NORMAL)
        elif initialize:
            self.__font_style = FontStyle.NORMAL

        font_weight = kwargs.get("font_weight")
        if font_weight:
            self.__font_weight = normalize_enum(font_weight, FontWeight, default=FontWeight.NORMAL)
        elif initialize:
            self.__font_weight = FontWeight.NORMAL

    def __update_align(self, initialize: bool, **kwargs) -> None:
        align = kwargs.get("align")
        if align:
            self.__align = normalize_enum(align, Align, default=Align.AUTO)
        elif initialize:
            self.__align = Align.AUTO

        valign = kwargs.get("vertical_align")
        if valign:
            self.__valign = normalize_enum(valign, VerticalAlign, default=VerticalAlign.BASELINE)
        elif initialize:
            self.__valign = VerticalAlign.BASELINE

    def __update_misc(self, initialize: bool, **kwargs) -> None:
        padding = kwargs.get("padding")
        if padding is not None:
            self.__padding = padding
        elif initialize:
            self.__padding = None

        decoration_line = kwargs.get("decoration_line")
        if decoration_line:
            self.__decoration_line = normalize_enum(
                decoration_line, DecorationLine, default=DecorationLine.NONE
            )
        elif initialize:
            self.__decoration_line = DecorationLine.NONE

        thousand_separator = kwargs.get("thousand_separator")
        if thousand_separator:
            self.__thousand_separator = _normalize_thousand_separator(
                normalize_enum(
                    thousand_separator,
                    ThousandSeparator,
                    default=ThousandSeparator.NONE,
                    validate=False,
                )
            )
        elif initialize:
            self.__thousand_separator = ThousandSeparator.NONE
        self.__validate_attr("thousand_separator", ThousandSeparator)

    def __validate_attr(self, attr_name: str, expected_type) -> None:
        value = getattr(self, attr_name)
        if isinstance(expected_type, (list, tuple)):
            expected = " or ".join(c.__name__ for c in expected_type)
        else:
            expected = expected_type.__name__

        if not isinstance(value, expected_type):
            raise TypeError(f"{attr_name} must be instance of {expected}: actual={type(value)}")
