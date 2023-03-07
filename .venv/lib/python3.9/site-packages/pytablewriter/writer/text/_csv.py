from typing import List

import typepy

from ._text_writer import TextTableWriter


class CsvTableWriter(TextTableWriter):
    """
    A table writer class for character separated values format.
    The default separated character is a comma (``","``).

        :Example:
            :ref:`example-csv-table-writer`
    """

    FORMAT_NAME = "csv"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return True

    @property
    def margin(self) -> int:
        return self._margin

    @margin.setter
    def margin(self, value: int) -> None:
        # margin setting must be ignored
        return

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._set_chars("")
        self.indent_string = ""
        self.column_delimiter = kwargs.get("column_delimiter", ",")
        self._margin = 0

        self.is_padding = False
        self.is_formatting_float = False
        self.is_write_header_separator_row = False

        self._quoting_flags[typepy.Typecode.NULL_STRING] = False

    def _write_header(self) -> None:
        if typepy.is_empty_sequence(self.headers):
            return

        super()._write_header()

    def _get_opening_row_items(self) -> List[str]:
        return []

    def _get_value_row_separator_items(self) -> List[str]:
        return []

    def _get_closing_row_items(self) -> List[str]:
        return []
