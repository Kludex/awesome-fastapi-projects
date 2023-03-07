import enum
import io
import sys
from itertools import chain
from typing import IO, List, Optional, Sequence, Union, cast

import typepy
from dataproperty import Align, ColumnDataProperty, DataProperty, LineBreakHandling

from ...error import EmptyTableDataError
from ...style import Cell, Style, StylerInterface, TextStyler
from ...style._styler import get_align_char
from .._common import HEADER_ROW
from .._table_writer import AbstractTableWriter, ColSeparatorStyleFilterFunc
from ._interface import IndentationInterface, TextWriterInterface


@enum.unique
class RowType(enum.Enum):
    OPENING = "opening"
    HEADER_SEPARATOR = "header separator"
    MIDDLE = "middle"
    CLOSING = "closing"


class TextTableWriter(AbstractTableWriter, TextWriterInterface):
    """
    A base class for table writer with text formats.

    .. figure:: ss/table_char.png
       :scale: 60%
       :alt: table_char

       Character attributes that compose a table

    .. py:attribute:: column_delimiter
        :type: str

        A column delimiter of a table.

    .. py:attribute:: char_left_side_row
        :type: str

        A character of a left side of a row.

    .. py:attribute:: char_right_side_row
        :type: str

        A character of a right side of a row.

    .. py:attribute:: char_cross_point
        :type: str

        A character of the crossing point of column delimiter and row
        delimiter.

    .. py:attribute:: char_opening_row
        :type: str

        A character of the first line of a table.

    .. py:attribute:: char_header_row_separator
        :type: str

        A character of a separator line of the header and
        the body of the table.

    .. py:attribute:: char_value_row_separator
        :type: str

        A character of a row separator line of the table.

    .. py:attribute:: char_closing_row
        :type: str

        A character of the last line of a table.

    .. py:attribute:: is_write_header_separator_row
        :type: bool

        Write a header separator line of the table if the value is |True|.

    .. py:attribute:: is_write_value_separator_row
        :type: bool

        Write row separator line(s) of the table if the value is |True|.

    .. py:attribute:: is_write_opening_row
        :type: bool

        Write an opening line of the table if the value is |True|.

    .. py:attribute:: is_write_closing_row
        :type: bool

        Write a closing line of the table if the value is |True|.

    .. py:attribute:: is_write_null_line_after_table
        :type: bool

        Write a blank line of after writing a table if the value is |True|.

    .. py:attribute:: margin
        :type: int

        Margin size for each cells

    """

    def __update_template(self) -> None:
        self.__value_cell_margin_format = self.__make_margin_format(" ")
        self.__opening_row_cell_format = self.__make_margin_format(self.char_opening_row)
        self._header_row_separator_cell_format = self.__make_margin_format(
            self.char_header_row_separator
        )
        self.__value_row_separator_cell_format = self.__make_margin_format(
            self.char_value_row_separator
        )
        self.__closing_row_cell_format = self.__make_margin_format(self.char_closing_row)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.stream = sys.stdout

        self._set_chars("")

        self.column_delimiter = "|"

        self.char_opening_row = "-"
        self.char_opening_row_cross_point = "-"

        self.char_header_row_separator = "-"
        self.char_header_row_cross_point = "-"

        self.char_value_row_separator = "-"

        self.char_closing_row = "-"
        self.char_closing_row_cross_point = "-"

        self._margin = kwargs.get("margin", 0)

        self._dp_extractor.preprocessor.line_break_handling = LineBreakHandling.REPLACE
        self.is_write_null_line_after_table = kwargs.get("is_write_null_line_after_table", False)

        self._init_cross_point_maps()

        self._col_separator_style_filters: List[ColSeparatorStyleFilterFunc] = []

        if "theme" in kwargs:
            self.set_theme(kwargs["theme"])

    def __repr__(self) -> str:
        return self.dumps()

    @property
    def margin(self) -> int:
        return self._margin

    @margin.setter
    def margin(self, value: int) -> None:
        if value < 0:
            raise ValueError("margin value must be zero or greater")

        if self._margin == value:
            return

        self._margin = value
        self._clear_preprocess()

    def _init_cross_point_maps(self) -> None:
        self.__cross_point_maps = {
            RowType.OPENING: self.char_opening_row_cross_point,
            RowType.HEADER_SEPARATOR: self.char_header_row_cross_point,
            RowType.MIDDLE: self.char_cross_point,
            RowType.CLOSING: self.char_closing_row_cross_point,
        }
        self.__left_cross_point_maps = {
            RowType.OPENING: self.char_top_left_cross_point,
            RowType.HEADER_SEPARATOR: self.char_header_row_left_cross_point,
            RowType.MIDDLE: self.char_left_cross_point,
            RowType.CLOSING: self.char_bottom_left_cross_point,
        }
        self.__right_cross_point_maps = {
            RowType.OPENING: self.char_top_right_cross_point,
            RowType.HEADER_SEPARATOR: self.char_header_row_right_cross_point,
            RowType.MIDDLE: self.char_right_cross_point,
            RowType.CLOSING: self.char_bottom_right_cross_point,
        }

    def add_col_separator_style_filter(self, style_filter: ColSeparatorStyleFilterFunc) -> None:
        """Add a style filter function for columns to the writer.

        Args:
            style_filter:
                A function that called for each cell in the table to apply a style
                to table cells.
                The function will be required to implement the following Protocol:

                .. code-block:: python

                    class ColSeparatorStyleFilterFunc(Protocol):
                        def __call__(
                            self, left_cell: Optional[Cell], right_cell: Optional[Cell], **kwargs: Dict[str, Any]
                        ) -> Optional[Style]:
                            ...

                If more than one style filter function is added to the writer,
                it will be called from the last one added.
                These style functions should return |None| when not needed to apply styles.
                If all of the style functions returned |None|,
                :py:attr:`~.default_style` will be applied.

                You can pass keyword arguments to style filter functions via
                :py:attr:`~.style_filter_kwargs`. In default, the attribute includes:

                    - ``writer``: the writer instance that the caller of a ``style_filter function``
        """

        self._col_separator_style_filters.insert(0, style_filter)
        self._clear_preprocess()

    def clear_theme(self) -> None:
        """Remove all of the style filters."""

        super().clear_theme()

        if not self._col_separator_style_filters:
            return

        self._col_separator_style_filters = []
        self._clear_preprocess()

    def write_null_line(self) -> None:
        """
        Write a null line to the |stream|.
        """

        self._write_line()

    def write_table(self, **kwargs) -> None:
        """
        |write_table|.

        .. note::
            - |None| values are written as an empty string.
        """

        try:
            super().write_table(**kwargs)
        except EmptyTableDataError:
            raise

        if self.is_write_null_line_after_table:
            self.write_null_line()

    def dump(self, output: Union[str, IO], close_after_write: bool = True, **kwargs) -> None:
        """Write data to the output with tabular format.

        During the executing this method,
        :py:attr:`~pytablewriter.writer._table_writer.AbstractTableWriter.enable_ansi_escape`
        attribute will be temporarily set to |False|.

        Args:
            output:
                The value must either an output stream or a path to an output file.

            close_after_write:
                Close the output after write.
                Defaults to |True|.
        """

        try:
            output.write  # type: ignore
            self.stream = output
        except AttributeError:
            self.stream = open(output, "w", encoding="utf-8")  # type: ignore

        try:
            stash = self.enable_ansi_escape
            self.enable_ansi_escape = False
            self.write_table(**kwargs)
        finally:
            if close_after_write:
                self.stream.close()  # type: ignore
                self.stream = sys.stdout

            self.enable_ansi_escape = stash

    def dumps(self, **kwargs) -> str:
        """Get rendered tabular text from the table data.

        Only available for text format table writers.

        Args:
            **kwargs:
                Optional arguments that the writer takes.

        Returns:
            str: Rendered tabular text.
        """

        old_stream = self.stream

        try:
            self.stream = io.StringIO()
            self.write_table(**kwargs)
            tabular_text = self.stream.getvalue()
        finally:
            self.stream = old_stream

        return tabular_text

    def _set_chars(self, c: str) -> None:
        self.char_left_side_row = c
        self.char_right_side_row = c

        self.char_cross_point = c
        self.char_left_cross_point = c
        self.char_right_cross_point = c
        self.char_top_left_cross_point = c
        self.char_top_right_cross_point = c
        self.char_bottom_left_cross_point = c
        self.char_bottom_right_cross_point = c

        self.char_opening_row = c
        self.char_opening_row_cross_point = c

        self.char_header_row_separator = c
        self.char_header_row_cross_point = c
        self.char_header_row_left_cross_point = c
        self.char_header_row_right_cross_point = c

        self.char_value_row_separator = c

        self.char_closing_row = c
        self.char_closing_row_cross_point = c

        self._init_cross_point_maps()

    def _create_styler(self, writer: AbstractTableWriter) -> StylerInterface:
        return TextStyler(writer)

    def _write_table_iter(self, **kwargs) -> None:
        super()._write_table_iter()
        if self.is_write_null_line_after_table:
            self.write_null_line()

    def _write_table(self, **kwargs) -> None:
        self._preprocess()
        self._write_opening_row()

        try:
            self._write_header()
            self.__write_header_row_separator()
        except ValueError:
            pass

        is_first_value_row = True
        for row, (values, value_dp_list) in enumerate(
            zip(self._table_value_matrix, self._table_value_dp_matrix)
        ):
            try:
                if is_first_value_row:
                    is_first_value_row = False
                else:
                    if self.is_write_value_separator_row:
                        self._write_value_row_separator()

                self._write_value_row(row, cast(List[str], values), value_dp_list)
            except TypeError:
                continue

        self._write_closing_row()

    def _get_opening_row_items(self) -> List[str]:
        return self.__get_row_separator_items(self.__opening_row_cell_format, self.char_opening_row)

    def _get_header_row_separator_items(self) -> List[str]:
        return self.__get_row_separator_items(
            self._header_row_separator_cell_format, self.char_header_row_separator
        )

    def _get_value_row_separator_items(self) -> List[str]:
        return self.__get_row_separator_items(
            self.__value_row_separator_cell_format, self.char_value_row_separator
        )

    def _get_closing_row_items(self) -> List[str]:
        return self.__get_row_separator_items(self.__closing_row_cell_format, self.char_closing_row)

    def __get_row_separator_items(self, margin_format: str, separator_char: str) -> List[str]:
        return [
            margin_format.format(separator_char * self._get_padding_len(col_dp))
            for col_dp in self._column_dp_list
        ]

    def _get_header_format_string(self, col_dp: ColumnDataProperty, value_dp: DataProperty) -> str:
        return "{{:{:s}{:s}}}".format(
            get_align_char(Align.CENTER),
            str(self._get_padding_len(col_dp, value_dp)),
        )

    def _to_header_item(self, col_dp: ColumnDataProperty, value_dp: DataProperty) -> str:
        return self.__value_cell_margin_format.format(super()._to_header_item(col_dp, value_dp))

    def _apply_style_to_row_item(
        self, row_idx: int, col_dp: ColumnDataProperty, value_dp: DataProperty, style: Style
    ) -> str:
        return self.__value_cell_margin_format.format(
            super()._apply_style_to_row_item(row_idx, col_dp, value_dp, style)
        )

    def _write_raw_string(self, unicode_text: str) -> None:
        self.stream.write(unicode_text)

    def _write_raw_line(self, unicode_text: str = "") -> None:
        self._write_raw_string(unicode_text + "\n")

    def _write(self, text):
        self._write_raw_string(text)

    def _write_line(self, text: str = "") -> None:
        self._write_raw_line(text)

    def _fetch_col_separator_style(
        self, left_cell: Optional[Cell], right_cell: Optional[Cell], default_style: Style
    ) -> Style:
        for style_filter in self._col_separator_style_filters:
            style = style_filter(left_cell, right_cell, **self.style_filter_kwargs)
            if style:
                return style

        return default_style

    def __to_column_delimiter(
        self,
        row: int,
        left_col_dp: Optional[ColumnDataProperty],
        right_col_dp: Optional[ColumnDataProperty],
        col_delimiter: str,
    ) -> str:
        left_cell = None
        if left_col_dp:
            left_cell = Cell(
                row=row,
                col=left_col_dp.column_index,
                value=col_delimiter,
                default_style=self._get_col_style(left_col_dp.column_index),
            )

        right_cell = None
        if right_col_dp:
            right_cell = Cell(
                row=row,
                col=right_col_dp.column_index,
                value=col_delimiter,
                default_style=self._get_col_style(right_col_dp.column_index),
            )

        style = self._fetch_col_separator_style(
            left_cell=left_cell,
            right_cell=right_cell,
            default_style=self.default_style,
        )

        return self._styler.apply_terminal_style(col_delimiter, style=style)

    def _write_row(self, row: int, values: Sequence[str]) -> None:
        if typepy.is_empty_sequence(values):
            return

        col_delimiters = (
            [
                self.__to_column_delimiter(
                    row,
                    None,
                    self._column_dp_list[0],
                    self.char_left_side_row,
                )
            ]
            + [
                self.__to_column_delimiter(
                    row,
                    self._column_dp_list[col_idx],
                    self._column_dp_list[col_idx + 1],
                    self.column_delimiter,
                )
                for col_idx in range(len(self._column_dp_list) - 1)
            ]
            + [
                self.__to_column_delimiter(
                    row,
                    self._column_dp_list[-1],
                    None,
                    self.char_right_side_row,
                )
            ]
        )

        row_items = [""] * (len(col_delimiters) + len(values))
        row_items[::2] = col_delimiters
        row_items[1::2] = list(values)

        self._write_line("".join(chain.from_iterable(row_items)))

    def _write_header(self) -> None:
        if not self.is_write_header:
            return

        if typepy.is_empty_sequence(self._table_headers):
            raise ValueError("header is empty")

        self._write_row(HEADER_ROW, self._table_headers)

    def _write_value_row(
        self, row: int, values: Sequence[str], value_dp_list: Sequence[DataProperty]
    ) -> None:
        self._write_row(row, values)

    def __write_separator_row(self, values, row_type=RowType.MIDDLE):
        if typepy.is_empty_sequence(values):
            return

        cross_point = self.__cross_point_maps[row_type]
        left_cross_point = self.__left_cross_point_maps[row_type]
        right_cross_point = self.__right_cross_point_maps[row_type]

        left_cross_point = left_cross_point if left_cross_point else cross_point
        right_cross_point = right_cross_point if right_cross_point else cross_point
        if typepy.is_null_string(self.char_left_side_row):
            left_cross_point = ""
        if typepy.is_null_string(self.char_right_side_row):
            right_cross_point = ""

        self._write_line(left_cross_point + cross_point.join(values) + right_cross_point)

    def _write_opening_row(self) -> None:
        if not self.is_write_opening_row:
            return

        self.__write_separator_row(self._get_opening_row_items(), row_type=RowType.OPENING)

    def __write_header_row_separator(self):
        if any([not self.is_write_header, not self.is_write_header_separator_row]):
            return

        self.__write_separator_row(
            self._get_header_row_separator_items(), row_type=RowType.HEADER_SEPARATOR
        )

    def _write_value_row_separator(self) -> None:
        """
        Write row separator of the table which matched to the table type
        regardless of the value of the
        :py:attr:`.is_write_value_separator_row`.
        """

        self.__write_separator_row(self._get_value_row_separator_items())

    def _write_closing_row(self) -> None:
        if not self.is_write_closing_row:
            return

        self.__write_separator_row(self._get_closing_row_items(), row_type=RowType.CLOSING)

    def __make_margin_format(self, margin_char):
        margin_str = margin_char * self._margin

        return margin_str + "{:s}" + margin_str

    def _preprocess_table_property(self) -> None:
        super()._preprocess_table_property()

        self.__update_template()
        self._init_cross_point_maps()


class IndentationTextTableWriter(TextTableWriter, IndentationInterface):
    """A base class for table writer with indentation text formats.

    Args:
        indent_level (int): Indentation level. Defaults to ``0``.

    .. py:attribute:: indent_string

        Indentation string for each level.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.set_indent_level(kwargs.get("indent_level", 0))
        self.indent_string = kwargs.get("indent_string", "")

    def set_indent_level(self, indent_level: int) -> None:
        """Set the indentation level.

        Args:
            indent_level (int): New indentation level.
        """

        self._indent_level = indent_level

    def inc_indent_level(self) -> None:
        """Increment the indentation level."""

        self._indent_level += 1

    def dec_indent_level(self) -> None:
        """Decrement the indentation level."""

        self._indent_level -= 1

    def write_table(self, **kwargs) -> None:
        """
        |write_table|.

        Args:
            indent (Optional[int]):
                Indent level of an output.
                Interpretation of indent level value differ format to format.
                Some writer classes may ignore this value.

        .. note::
            - |None| values are written as an empty string.
        """

        indent = kwargs.pop("indent", None)

        if indent is not None:
            self._logger.logger.debug(f"indent: {indent}")
            self.set_indent_level(int(indent))

        try:
            super().write_table(**kwargs)
        except EmptyTableDataError:
            self._logger.logger.debug("no tabular data found")
            return

    def _get_indent_string(self) -> str:
        return self.indent_string * self._indent_level

    def _write(self, text):
        self._write_raw_string(self._get_indent_string() + text)

    def _write_line(self, text: str = "") -> None:
        if typepy.is_not_null_string(text):
            self._write_raw_line(self._get_indent_string() + text)
        else:
            self._write_raw_line("")
