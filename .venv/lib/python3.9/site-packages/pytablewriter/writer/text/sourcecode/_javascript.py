import io
from typing import List

from dataproperty import ColumnDataProperty, DataProperty, DefaultValue
from typepy import StrictLevel, Typecode

from ...._converter import strip_quote
from ...._function import quote_datetime_formatter
from ....sanitizer import sanitize_js_var_name
from .._common import bool_to_str
from ._sourcecode import SourceCodeTableWriter


def js_datetime_formatter(value) -> str:
    try:
        return f'new Date("{value.strftime(DefaultValue.DATETIME_FORMAT):s}")'
    except ValueError:
        # the datetime strftime() methods require year >= 1900
        return f'new Date("{value}")'


class JavaScriptTableWriter(SourceCodeTableWriter):
    """
    A table writer for class JavaScript format.

        :Example:
            :ref:`example-js-table-writer`

    .. py:attribute:: variable_declaration
        :type: str
        :value: "const"

        JavaScript variable declarations type.
        The value must be either ``"var"``, ``"let"`` or ``"const"``.

    .. py:method:: write_table

        |write_table| with JavaScript format.
        The tabular data are written as a nested list variable definition.

        :raises pytablewriter.EmptyTableNameError:
            If the |table_name| is empty.
        :Example:
            :ref:`example-js-table-writer`

        .. note::
            Specific values in the tabular data are converted when writing:

            - |None|: written as ``null``
            - |inf|: written as ``Infinity``
            - |nan|: written as ``NaN``
            - |datetime| instances determined by |is_datetime_instance_formatting| attribute:
                - |True|: written as `dateutil.parser <https://dateutil.readthedocs.io/en/stable/parser.html>`__
                - |False|: written as |str|

            .. seealso::
                :ref:`example-type-hint-js`
    """

    FORMAT_NAME = "javascript"
    __VALID_VAR_DECLARATION = ("var", "let", "const")
    __NONE_VALUE_DP = DataProperty("null")

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return True

    @property
    def variable_declaration(self) -> str:
        return self.__variable_declaration

    @variable_declaration.setter
    def variable_declaration(self, value: str):
        value = value.strip().casefold()
        if value not in self.__VALID_VAR_DECLARATION:
            raise ValueError("declaration must be either var, let or const")

        self.__variable_declaration = value

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.variable_declaration = "const"
        self._dp_extractor.type_value_map = {
            # Typecode.NONE: "null",
            Typecode.INFINITY: "Infinity",
            Typecode.NAN: "NaN",
        }
        self._dp_extractor.update_strict_level_map({Typecode.BOOL: StrictLevel.MAX})
        self.register_trans_func(bool_to_str)

    def get_variable_name(self, value: str) -> str:
        return sanitize_js_var_name(value, "_").casefold()

    def _write_table(self, **kwargs) -> None:
        if self.is_datetime_instance_formatting:
            self._dp_extractor.datetime_formatter = js_datetime_formatter
        else:
            self._dp_extractor.datetime_formatter = quote_datetime_formatter

        org_stream = self.stream
        self.stream = io.StringIO()

        self.inc_indent_level()
        super()._write_table(**kwargs)
        self.dec_indent_level()
        js_matrix_var_def_text = self.stream.getvalue().rstrip("\n")
        js_matrix_var_def_text = strip_quote(js_matrix_var_def_text, "true")
        js_matrix_var_def_text = strip_quote(js_matrix_var_def_text, "false")
        if self.is_write_closing_row:
            js_matrix_var_def_line_list = js_matrix_var_def_text.splitlines()
            js_matrix_var_def_line_list[-2] = js_matrix_var_def_line_list[-2].rstrip(",")
            js_matrix_var_def_text = "\n".join(js_matrix_var_def_line_list)

        self.stream.close()
        self.stream = org_stream

        self.dec_indent_level()
        self._write_line(js_matrix_var_def_text)
        self.inc_indent_level()

    def _get_opening_row_items(self) -> List[str]:
        return [f"{self.variable_declaration:s} {self.variable_name:s} = ["]

    def _get_closing_row_items(self) -> List[str]:
        return ["];"]

    def _to_row_item(self, row_idx: int, col_dp: ColumnDataProperty, value_dp: DataProperty) -> str:
        if value_dp.data is None:
            value_dp = self.__NONE_VALUE_DP

        return super()._to_row_item(row_idx, col_dp, value_dp)
