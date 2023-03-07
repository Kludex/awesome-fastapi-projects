import copy
from textwrap import indent
from typing import List

import dataproperty
import typepy
from dataproperty import ColumnDataProperty, DataProperty
from mbstrdecoder import MultiByteStrDecoder
from tabledata import to_value_matrix
from typepy import Typecode

from .._msgfy import to_error_message
from ._common import serialize_dp
from ._text_writer import IndentationTextTableWriter


try:
    import simplejson as json
except ImportError:
    import json  # type: ignore


class JsonTableWriter(IndentationTextTableWriter):
    """
    A table writer class for JSON format.

        :Examples:
            :ref:`example-json-table-writer`

    .. py:method:: write_table

        |write_table| with JSON format.

        Args:
            indent (Optional[int]):
                Indent level of an output.
                Interpretation of indent level value differ format to format.
                Some writer classes may ignore this value.
                Defaults to 4.

            sort_keys (Optional[bool]):
                If |True|, the output of dictionaries will be sorted by key.
                Defaults to |False|.

        Examples:
            :ref:`example-json-table-writer`

        .. note::
            Specific values in the tabular data are converted when writing:

            - |None|: written as ``null``
            - |inf|: written as ``Infinity``
            - |nan|: written as ``NaN``
    """

    FORMAT_NAME = "json"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.set_indent_level(4)

        self.is_formatting_float = False
        self.is_write_opening_row = True
        self.is_write_closing_row = True
        self.char_right_side_row = ","
        self.char_opening_row_cross_point = ""
        self.char_closing_row_cross_point = ""

        self._is_require_header = True
        self._dp_extractor.type_value_map = {
            Typecode.INFINITY: "Infinity",
            Typecode.NAN: "NaN",
        }
        self._dp_extractor.update_strict_level_map({Typecode.BOOL: typepy.StrictLevel.MAX})
        self._quoting_flags = copy.deepcopy(dataproperty.NOT_QUOTING_FLAGS)

        self._init_cross_point_maps()

    def write_null_line(self) -> None:
        self._verify_stream()
        self.stream.write("\n")

    def _write_table(self, **kwargs) -> None:
        sort_keys = kwargs.get("sort_keys", False)

        self._preprocess()

        with self._logger:
            self._write_opening_row()

            json_text_list = []
            for json_data in self._table_value_matrix:
                json_text = json.dumps(
                    json_data, indent=self._indent_level, ensure_ascii=False, sort_keys=sort_keys
                )
                json_text_list.append(json_text)

            joint_text = self.char_right_side_row + "\n"
            json_text = joint_text.join(json_text_list)
            if all([not self.is_write_closing_row, typepy.is_not_null_string(json_text)]):
                json_text += joint_text

            self.stream.write(indent(json_text, " " * self._indent_level))
            self._write_closing_row()

    def _to_row_item(self, row_idx: int, col_dp: ColumnDataProperty, value_dp: DataProperty) -> str:
        return value_dp.to_str()

    def _preprocess_table_dp(self) -> None:
        if self._is_complete_table_dp_preprocess:
            return

        self._logger.logger.debug("_preprocess_table_dp")

        try:
            self._table_value_dp_matrix = self._dp_extractor.to_dp_matrix(
                to_value_matrix(self.headers, self.value_matrix)
            )
        except TypeError as e:
            self._logger.logger.debug(to_error_message(e))
            self._table_value_dp_matrix = []

        self._is_complete_table_dp_preprocess = True

    def _preprocess_header(self) -> None:
        if self._is_complete_header_preprocess:
            return

        self._logger.logger.debug("_preprocess_header")

        self._table_headers = [
            header_dp.to_str() for header_dp in self._dp_extractor.to_header_dp_list()
        ]

        self._is_complete_header_preprocess = True

    def _preprocess_value_matrix(self) -> None:
        if self._is_complete_value_matrix_preprocess:
            return

        self._table_value_matrix = [
            dict(zip(self._table_headers, [serialize_dp(dp) for dp in dp_list]))
            for dp_list in self._table_value_dp_matrix
        ]

        self._is_complete_value_matrix_preprocess = True

    def _get_opening_row_items(self) -> List[str]:
        if typepy.is_not_null_string(self.table_name):
            return [f'{{ "{MultiByteStrDecoder(self.table_name).unicode_str:s}" : [']

        return ["["]

    def _get_closing_row_items(self) -> List[str]:
        if typepy.is_not_null_string(self.table_name):
            return ["\n]}"]

        return ["\n]"]
