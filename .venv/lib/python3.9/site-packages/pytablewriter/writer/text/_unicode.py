import copy

import dataproperty as dp

from ._text_writer import IndentationTextTableWriter


class UnicodeTableWriter(IndentationTextTableWriter):
    """
    A table writer class using Unicode characters.

        :Example:
            :ref:`example-unicode-table-writer`
    """

    FORMAT_NAME = "unicode"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.column_delimiter = "│"
        self.char_left_side_row = "│"
        self.char_right_side_row = "│"

        self.char_cross_point = "┼"
        self.char_left_cross_point = "├"
        self.char_right_cross_point = "┤"
        self.char_header_row_cross_point = "┼"
        self.char_header_row_left_cross_point = "├"
        self.char_header_row_right_cross_point = "┤"
        self.char_top_left_cross_point = "┌"
        self.char_top_right_cross_point = "┐"
        self.char_bottom_left_cross_point = "└"
        self.char_bottom_right_cross_point = "┘"

        self.char_opening_row = "─"
        self.char_opening_row_cross_point = "┬"

        self.char_header_row_separator = "─"
        self.char_value_row_separator = "─"

        self.char_closing_row = "─"
        self.char_closing_row_cross_point = "┴"

        self.indent_string = kwargs.get("indent_string", "    ")
        self.is_write_header_separator_row = True
        self.is_write_value_separator_row = True
        self.is_write_opening_row = True
        self.is_write_closing_row = True

        self._quoting_flags = copy.deepcopy(dp.NOT_QUOTING_FLAGS)

        self._init_cross_point_maps()


class BoldUnicodeTableWriter(IndentationTextTableWriter):
    """
    A table writer class using bold Unicode characters.

        :Example:
            :ref:`example-unicode-table-writer`
    """

    FORMAT_NAME = "bold_unicode"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.table_name = ""

        self.column_delimiter = "┃"
        self.char_left_side_row = "┃"
        self.char_right_side_row = "┃"

        self.char_cross_point = "╋"
        self.char_left_cross_point = "┣"
        self.char_right_cross_point = "┫"
        self.char_header_row_cross_point = "╋"
        self.char_header_row_left_cross_point = "┣"
        self.char_header_row_right_cross_point = "┫"
        self.char_top_left_cross_point = "┏"
        self.char_top_right_cross_point = "┓"
        self.char_bottom_left_cross_point = "┗"
        self.char_bottom_right_cross_point = "┛"

        self.char_opening_row = "━"
        self.char_opening_row_cross_point = "┳"

        self.char_header_row_separator = "━"
        self.char_value_row_separator = "━"

        self.char_closing_row = "━"
        self.char_closing_row_cross_point = "┻"

        self.indent_string = kwargs.get("indent_string", "    ")
        self.is_write_header_separator_row = True
        self.is_write_value_separator_row = True
        self.is_write_opening_row = True
        self.is_write_closing_row = True

        self._quoting_flags = copy.deepcopy(dp.NOT_QUOTING_FLAGS)

        self._init_cross_point_maps()
