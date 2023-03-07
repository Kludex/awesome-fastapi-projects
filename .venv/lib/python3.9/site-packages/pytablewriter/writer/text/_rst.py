import copy
from typing import List

import dataproperty
import typepy
from mbstrdecoder import MultiByteStrDecoder

from ...error import EmptyTableDataError
from ...style import ReStructuredTextStyler, StylerInterface
from .._table_writer import AbstractTableWriter
from ._text_writer import IndentationTextTableWriter


class RstTableWriter(IndentationTextTableWriter):
    """
    A base class of reStructuredText table writer.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.char_header_row_separator = "="
        self.char_cross_point = "+"
        self.char_left_cross_point = "+"
        self.char_right_cross_point = "+"
        self.char_top_left_cross_point = "+"
        self.char_top_right_cross_point = "+"
        self.char_bottom_left_cross_point = "+"
        self.char_bottom_right_cross_point = "+"
        self.char_header_row_cross_point = "+"
        self.char_header_row_left_cross_point = "+"
        self.char_header_row_right_cross_point = "+"

        self.char_opening_row_cross_point = "+"
        self.char_closing_row_cross_point = "+"

        self.indent_string = kwargs.get("indent_string", "    ")
        self.is_write_header_separator_row = True
        self.is_write_value_separator_row = True
        self.is_write_opening_row = True
        self.is_write_closing_row = True

        self._quoting_flags = copy.deepcopy(dataproperty.NOT_QUOTING_FLAGS)

        self._init_cross_point_maps()

    def write_table(self, **kwargs) -> None:
        with self._logger:
            self._write_line(self._get_table_directive())

            try:
                self._verify_property()
            except EmptyTableDataError:
                self._logger.logger.debug("no tabular data found")
                return

            self._write_table(**kwargs)
            if self.is_write_null_line_after_table:
                self.write_null_line()

    def _get_table_directive(self) -> str:
        if typepy.is_null_string(self.table_name):
            return ".. table::\n"

        return f".. table:: {MultiByteStrDecoder(self.table_name).unicode_str}\n"

    def _write_table(self, **kwargs) -> None:
        self.inc_indent_level()
        super()._write_table(**kwargs)
        self.dec_indent_level()

    def _create_styler(self, writer: AbstractTableWriter) -> StylerInterface:
        return ReStructuredTextStyler(writer)


class RstCsvTableWriter(RstTableWriter):
    """
    A table class writer for reStructuredText
    `CSV table <http://docutils.sourceforge.net/docs/ref/rst/directives.html#id4>`__
    format.

        :Example:
            :ref:`example-rst-csv-table-writer`
    """

    FORMAT_NAME = "rst_csv_table"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.column_delimiter = ", "
        self.char_cross_point = ""
        self.is_padding = False
        self.is_write_header_separator_row = False
        self.is_write_value_separator_row = False
        self.is_write_closing_row = False

        self._quoting_flags[typepy.Typecode.STRING] = True

    def write_table(self, **kwargs) -> None:
        """
        |write_table| with reStructuredText CSV table format.

        :Example:
            :ref:`example-rst-csv-table-writer`

        .. note::
            - |None| values are written as an empty string
        """

        IndentationTextTableWriter.write_table(self, **kwargs)

    def _get_opening_row_items(self) -> List[str]:
        directive = ".. csv-table::"

        if typepy.is_null_string(self.table_name):
            return [directive]

        return [f"{directive} {MultiByteStrDecoder(self.table_name).unicode_str}"]

    def _write_opening_row(self) -> None:
        self.dec_indent_level()
        super()._write_opening_row()
        self.inc_indent_level()

    def _write_header(self) -> None:
        if not self.is_write_header:
            return

        if typepy.is_not_empty_sequence(self.headers):
            self._write_line(
                ':header: "{:s}"'.format(
                    '", "'.join(MultiByteStrDecoder(header).unicode_str for header in self.headers)
                )
            )

        self._write_line(
            ":widths: " + ", ".join(str(col_dp.ascii_char_width) for col_dp in self._column_dp_list)
        )
        self._write_line()

    def _get_value_row_separator_items(self) -> List[str]:
        return []

    def _get_closing_row_items(self) -> List[str]:
        return []


class RstGridTableWriter(RstTableWriter):
    """
    A table writer class for reStructuredText
    `Grid Tables <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#grid-tables>`__
    format.

        :Example:
            :ref:`example-rst-grid-table-writer`

    .. py:method:: write_table

        |write_table| with reStructuredText grid tables format.

        :Example:
            :ref:`example-rst-grid-table-writer`

        .. note::
            - |None| values are written as an empty string
    """

    FORMAT_NAME = "rst_grid_table"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return False

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.char_left_side_row = "|"
        self.char_right_side_row = "|"


class RstSimpleTableWriter(RstTableWriter):
    """
    A table writer class for reStructuredText
    `Simple Tables
    <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#simple-tables>`__
    format.

        :Example:
            :ref:`example-rst-simple-table-writer`

    .. py:method:: write_table

        |write_table| with reStructuredText simple tables format.

        :Example:
            :ref:`example-rst-simple-table-writer`

        .. note::
            - |None| values are written as an empty string
    """

    FORMAT_NAME = "rst_simple_table"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return False

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.column_delimiter = "  "
        self.char_cross_point = "  "
        self.char_opening_row_cross_point = "  "
        self.char_closing_row_cross_point = "  "
        self.char_header_row_cross_point = "  "
        self.char_header_row_left_cross_point = "  "
        self.char_header_row_right_cross_point = "  "

        self.char_opening_row = "="
        self.char_closing_row = "="

        self.is_write_value_separator_row = False

        self._init_cross_point_maps()
