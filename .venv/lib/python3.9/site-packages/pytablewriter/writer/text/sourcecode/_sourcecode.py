import abc
from typing import List

import typepy

from .._text_writer import IndentationTextTableWriter


class SourceCodeTableWriter(IndentationTextTableWriter):
    """
    Base class of table writer with a source code (variable definition) format.

    .. py:attribute:: is_datetime_instance_formatting
        :type: bool

        Write |datetime| values in the table as definition of |datetime| class
        instances coincide with specific language if this value is |True|.
        Write as |str| if this value is |False|.
    """

    @abc.abstractmethod
    def get_variable_name(self, value: str) -> str:  # pragma: no cover
        pass

    @property
    def variable_name(self) -> str:
        """
        Return a valid variable name that converted from the |table_name|.

        :return: A variable name.
        :rtype: str
        """

        return self.get_variable_name(self.table_name)

    @property
    def margin(self) -> int:
        return self._margin

    @margin.setter
    def margin(self, value: int) -> None:
        # margin setting must be ignored
        return

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.indent_string = kwargs.get("indent_string", "    ")
        self.column_delimiter = ", "
        self._margin = 0

        self.char_left_side_row = "["
        self.char_right_side_row = "],"
        self.char_cross_point = ""
        self.char_opening_row_cross_point = ""
        self.char_closing_row_cross_point = ""

        self.is_padding = False
        self.is_write_header_separator_row = False
        self.is_write_opening_row = True
        self.is_write_closing_row = True

        self.is_formatting_float = False
        self.is_datetime_instance_formatting = True

        self._quoting_flags[typepy.Typecode.DATETIME] = False
        self._is_require_table_name = True

        self._init_cross_point_maps()

    def _get_value_row_separator_items(self) -> List[str]:
        return []

    def _write_opening_row(self) -> None:
        self.dec_indent_level()
        super()._write_opening_row()
        self.inc_indent_level()

    def _write_closing_row(self) -> None:
        self.dec_indent_level()
        super()._write_closing_row()
        self.inc_indent_level()
