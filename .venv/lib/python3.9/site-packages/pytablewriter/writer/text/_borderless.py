import copy

import dataproperty as dp

from ._text_writer import IndentationTextTableWriter


class BorderlessTableWriter(IndentationTextTableWriter):
    """
    A table writer class for borderless table.
    """

    FORMAT_NAME = "borderless"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.table_name = ""

        self.column_delimiter = ""
        self.char_left_side_row = ""
        self.char_right_side_row = ""

        self.indent_string = kwargs.get("indent_string", "    ")
        self.is_write_header_separator_row = False
        self.is_write_value_separator_row = False
        self.is_write_opening_row = False
        self.is_write_closing_row = False

        self._quoting_flags = copy.deepcopy(dp.NOT_QUOTING_FLAGS)

        self._init_cross_point_maps()
