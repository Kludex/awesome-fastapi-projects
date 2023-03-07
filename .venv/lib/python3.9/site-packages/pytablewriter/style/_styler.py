import abc
from typing import Any, Optional, cast

from tcolorpy import tcolor

from ._font import FontSize, FontStyle, FontWeight
from ._style import Align, DecorationLine, Style, ThousandSeparator


_align_char_mapping = {
    Align.AUTO: "<",
    Align.LEFT: "<",
    Align.RIGHT: ">",
    Align.CENTER: "^",
}


def get_align_char(align: Align) -> str:
    return _align_char_mapping[align]


class StylerInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def apply(self, value: Any, style: Style) -> str:  # pragma: no cover
        raise NotImplementedError()

    @abc.abstractmethod
    def apply_align(self, value: str, style: Style) -> str:  # pragma: no cover
        raise NotImplementedError()

    @abc.abstractmethod
    def apply_terminal_style(self, value: str, style: Style) -> str:  # pragma: no cover
        raise NotImplementedError()

    @abc.abstractmethod
    def get_font_size(self, style: Style) -> Optional[str]:  # pragma: no cover
        raise NotImplementedError()

    @abc.abstractmethod
    def get_additional_char_width(self, style: Style) -> int:  # pragma: no cover
        raise NotImplementedError()


class AbstractStyler(StylerInterface):
    def __init__(self, writer):
        self._writer = writer
        self._font_size_map = self._get_font_size_map()

    def get_font_size(self, style: Style) -> Optional[str]:
        return self._font_size_map.get(style.font_size)

    def get_additional_char_width(self, style: Style) -> int:
        return 0

    def apply(self, value: Any, style: Style) -> str:
        return value

    def apply_align(self, value: str, style: Style) -> str:
        return value

    def apply_terminal_style(self, value: str, style: Style) -> str:
        return value

    def _get_font_size_map(self):
        return {}


class NullStyler(AbstractStyler):
    def get_font_size(self, style: Style) -> Optional[str]:
        return ""


class TextStyler(AbstractStyler):
    def apply_terminal_style(self, value: str, style: Style) -> str:
        if not self._writer.enable_ansi_escape:
            return value

        ansi_styles = []

        if style.decoration_line in (DecorationLine.STRIKE, DecorationLine.LINE_THROUGH):
            ansi_styles.append("strike")
        if style.decoration_line == DecorationLine.UNDERLINE:
            ansi_styles.append("underline")

        if style.font_weight == FontWeight.BOLD:
            ansi_styles.append("bold")

        if self._writer.colorize_terminal:
            return tcolor(value, color=style.color, bg_color=style.bg_color, styles=ansi_styles)

        return tcolor(value, styles=ansi_styles)

    def __get_align_format(self, style: Style) -> str:
        align_char = get_align_char(style.align)
        format_items = ["{:" + align_char]
        if style.padding is not None and style.padding > 0:
            format_items.append(str(style.padding))
        format_items.append("s}")

        return "".join(format_items)

    def apply_align(self, value: str, style: Style) -> str:
        return self.__get_align_format(style).format(value)

    def apply(self, value: Any, style: Style) -> str:
        if value:
            if style.thousand_separator == ThousandSeparator.SPACE:
                value = value.replace(",", " ")
            elif style.thousand_separator == ThousandSeparator.UNDERSCORE:
                value = value.replace(",", "_")

        return value


class HtmlStyler(TextStyler):
    def _get_font_size_map(self):
        return {
            FontSize.TINY: "font-size:x-small",
            FontSize.SMALL: "font-size:small",
            FontSize.MEDIUM: "font-size:medium",
            FontSize.LARGE: "font-size:large",
        }


class LatexStyler(TextStyler):
    class Command:
        BOLD = r"\bf"
        ITALIC = r"\it"

    def get_additional_char_width(self, style: Style) -> int:
        width = 0

        if self.get_font_size(style):
            width += len(cast(str, self.get_font_size(style)))

        if style.font_weight == FontWeight.BOLD:
            width += len(self.Command.BOLD)

        if style.font_style == FontStyle.ITALIC:
            width += len(self.Command.ITALIC)

        return width

    def apply(self, value: Any, style: Style) -> str:
        value = super().apply(value, style)
        if not value:
            return value

        font_size = self.get_font_size(style)
        item_list = []

        if font_size:
            item_list.append(font_size)

        if style.font_weight == FontWeight.BOLD:
            item_list.append(self.Command.BOLD)

        if style.font_style == FontStyle.ITALIC:
            item_list.append(self.Command.ITALIC)

        item_list.append(value)
        return " ".join(item_list)

    def _get_font_size_map(self):
        return {
            FontSize.TINY: r"\tiny",
            FontSize.SMALL: r"\small",
            FontSize.MEDIUM: r"\normalsize",
            FontSize.LARGE: r"\large",
        }


class MarkdownStyler(TextStyler):
    def get_additional_char_width(self, style: Style) -> int:
        width = 0

        if style.font_weight == FontWeight.BOLD:
            width += 4

        if style.font_style == FontStyle.ITALIC:
            width += 2

        return width

    def apply(self, value: Any, style: Style) -> str:
        value = super().apply(value, style)
        if not value:
            return value

        if style.font_weight == FontWeight.BOLD:
            value = f"**{value}**"

        if style.font_style == FontStyle.ITALIC:
            value = f"_{value}_"

        return value


class GFMarkdownStyler(MarkdownStyler):
    """
    A styler class for GitHub Flavored Markdown
    """

    def get_additional_char_width(self, style: Style) -> int:
        width = super().get_additional_char_width(style)

        if style.decoration_line in (DecorationLine.STRIKE, DecorationLine.LINE_THROUGH):
            width += 4

        return width

    def apply(self, value: Any, style: Style) -> str:
        value = super().apply(value, style)
        if not value:
            return value

        if style.decoration_line in (DecorationLine.STRIKE, DecorationLine.LINE_THROUGH):
            value = f"~~{value}~~"

        return value


class ReStructuredTextStyler(TextStyler):
    def get_additional_char_width(self, style: Style) -> int:
        from ..writer import RstCsvTableWriter

        width = 0

        if style.font_weight == FontWeight.BOLD:
            width += 4
        elif style.font_style == FontStyle.ITALIC:
            width += 2

        if (
            style.thousand_separator == ThousandSeparator.COMMA
            and self._writer.format_name == RstCsvTableWriter.FORMAT_NAME
        ):
            width += 2

        return width

    def apply(self, value: Any, style: Style) -> str:
        from ..writer import RstCsvTableWriter

        value = super().apply(value, style)
        if not value:
            return value

        if style.font_weight == FontWeight.BOLD:
            value = f"**{value}**"
        elif style.font_style == FontStyle.ITALIC:
            # in reStructuredText, some custom style definition will be required to
            # set for both bold and italic (currently not supported)
            value = f"*{value}*"

        if (
            style.thousand_separator == ThousandSeparator.COMMA
            and self._writer.format_name == RstCsvTableWriter.FORMAT_NAME
        ):
            value = f'"{value}"'

        return value
