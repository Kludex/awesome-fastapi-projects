import copy
from typing import Any, List, Sequence

import dataproperty as dp
import typepy
from dataproperty import ColumnDataProperty, DataProperty, LineBreakHandling
from mbstrdecoder import MultiByteStrDecoder

from ...style import Align, FontStyle, FontWeight, Style, StylerInterface, TextStyler
from ...style._styler import get_align_char
from .._table_writer import AbstractTableWriter
from ._text_writer import TextTableWriter


class AsciiDocStyler(TextStyler):
    def apply(self, value: Any, style: Style) -> str:
        value = super().apply(value, style)
        if not value:
            return value

        try:
            fg_color = style.fg_color.name.lower()  # type: ignore
        except AttributeError:
            fg_color = None

        try:
            bg_color = style.bg_color.name.lower()  # type: ignore
        except AttributeError:
            bg_color = None

        if fg_color and bg_color:
            value = f"[{fg_color} {bg_color}-background]##{value}##"
        elif fg_color:
            value = f"[{fg_color}]##{value}##"
        elif bg_color:
            value = f"[{bg_color}-background]##{value}##"

        if style.font_weight == FontWeight.BOLD:
            value = f"*{value}*"

        if style.font_style == FontStyle.ITALIC:
            value = f"_{value}_"

        return value


class AsciiDocTableWriter(TextTableWriter):
    """
    A table writer class for `AsciiDoc <https://asciidoc.org/>`__ format.
    """

    FORMAT_NAME = "asciidoc"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.column_delimiter = "\n"

        self.is_padding = False
        self.is_write_header_separator_row = True
        self.is_write_value_separator_row = True
        self.is_write_opening_row = True
        self.is_write_closing_row = True

        self.update_preprocessor(line_break_handling=LineBreakHandling.NOP)

        self._quoting_flags = copy.deepcopy(dp.NOT_QUOTING_FLAGS)

    def _create_styler(self, writer: AbstractTableWriter) -> StylerInterface:
        return AsciiDocStyler(writer)

    def _write_value_row(
        self, row: int, values: Sequence[str], value_dp_list: Sequence[DataProperty]
    ) -> None:
        self._write_row(
            row,
            [
                self.__modify_row_element(row, col_idx, value, value_dp)
                for col_idx, (value, value_dp), in enumerate(zip(values, value_dp_list))
            ],
        )

    def _get_opening_row_items(self) -> List[str]:
        cols = ", ".join(
            f"{get_align_char(col_dp.align)}{col_dp.ascii_char_width}"
            for col_dp in self._column_dp_list
        )
        rows = [f'[cols="{cols}", options="header"]']

        if typepy.is_not_null_string(self.table_name):
            rows.append("." + MultiByteStrDecoder(self.table_name).unicode_str)

        rows.append("|===")

        return ["\n".join(rows)]

    def _get_header_row_separator_items(self) -> List[str]:
        return [""]

    def _get_value_row_separator_items(self) -> List[str]:
        return self._get_header_row_separator_items()

    def _get_closing_row_items(self) -> List[str]:
        return ["|==="]

    def _get_header_format_string(self, col_dp: ColumnDataProperty, value_dp: DataProperty) -> str:
        return f"{get_align_char(Align.CENTER)}|{{}}"

    def __modify_row_element(self, row_idx: int, col_idx: int, value: str, value_dp: DataProperty):
        default_style = self._get_col_style(col_idx)
        col_dp = self._column_dp_list[col_idx]
        style = self._fetch_style_from_filter(row_idx, col_dp, value_dp, default_style)
        align = col_dp.align

        if style and style.align and style.align != align:
            forma_stirng = "{0:s}|{1:s}"
            align = style.align
        elif value_dp.align != align:
            forma_stirng = "{0:s}|{1:s}"
            align = value_dp.align
        else:
            forma_stirng = "|{1:s}"

        return forma_stirng.format(get_align_char(align), value)
