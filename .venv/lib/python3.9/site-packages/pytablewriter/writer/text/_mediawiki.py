import copy
import re
from typing import List, Sequence

import dataproperty as dp
import typepy
from dataproperty import ColumnDataProperty, DataProperty, LineBreakHandling
from mbstrdecoder import MultiByteStrDecoder

from ...style import Align
from ...style._styler import get_align_char
from ._text_writer import TextTableWriter


class MediaWikiTableWriter(TextTableWriter):
    """
    A table writer class for `MediaWiki <https://www.mediawiki.org/wiki/MediaWiki>`__ format.

        :Example:
            :ref:`example-mediawiki-table-writer`
    """

    FORMAT_NAME = "mediawiki"
    __RE_TABLE_SEQUENCE = re.compile(r"^[\s]+[*|#]+")

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

        # experimental: This attribute may change in the future release
        self.table_style = kwargs.get("table_style", "")

    def _write_header(self) -> None:
        if not self.is_write_header:
            return

        if typepy.is_not_null_string(self.table_name):
            self._write_line("|+" + MultiByteStrDecoder(self.table_name).unicode_str)

        super()._write_header()

    def _write_value_row(
        self, row: int, values: Sequence[str], value_dp_list: Sequence[DataProperty]
    ) -> None:
        self._write_row(
            row,
            [
                self.__modify_table_element(value, value_dp)
                for value, value_dp, in zip(values, value_dp_list)
            ],
        )

    def _get_opening_row_items(self) -> List[str]:
        item = '{| class="wikitable"'
        if self.table_style:
            item += f' style="{self.table_style}"'

        return [item]

    def _get_header_row_separator_items(self) -> List[str]:
        return ["|-"]

    def _get_value_row_separator_items(self) -> List[str]:
        return self._get_header_row_separator_items()

    def _get_closing_row_items(self) -> List[str]:
        return ["|}"]

    def _get_header_format_string(self, col_dp: ColumnDataProperty, value_dp: DataProperty) -> str:
        return "! {{:{:s}{:s}}}".format(
            get_align_char(Align.CENTER), str(self._get_padding_len(col_dp, value_dp))
        )

    def __modify_table_element(self, value: str, value_dp: DataProperty):
        if value_dp.align is Align.LEFT:
            forma_stirng = "| {1:s}"
        else:
            forma_stirng = '| style="text-align:{0:s}"| {1:s}'

        if self.__RE_TABLE_SEQUENCE.search(value) is not None:
            value = "\n" + value.lstrip()

        return forma_stirng.format(value_dp.align.align_string, value)
