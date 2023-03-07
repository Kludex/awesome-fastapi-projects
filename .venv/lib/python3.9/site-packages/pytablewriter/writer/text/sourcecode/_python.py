from typing import List

import typepy

from ...._function import dateutil_datetime_formatter, quote_datetime_formatter
from ....sanitizer import sanitize_python_var_name
from ._sourcecode import SourceCodeTableWriter


class PythonCodeTableWriter(SourceCodeTableWriter):
    """
    A table writer class for Python source code format.

        :Example:
            :ref:`example-python-code-table-writer`

    .. py:method:: write_table

        |write_table| with Python format.
        The tabular data are written as a nested list variable definition
        for Python format.

        :raises pytablewriter.EmptyTableNameError:
            If the |table_name| is empty.
        :Example:
            :ref:`example-python-code-table-writer`

        .. note::
            Specific values in the tabular data are converted when writing:

            - |None|: written as ``None``
            - |inf|: written as ``float("inf")``
            - |nan|: written as ``float("nan")``
            - |datetime| instances determined by |is_datetime_instance_formatting| attribute:
                - |True|: written as `dateutil.parser <https://dateutil.readthedocs.io/en/stable/parser.html>`__
                - |False|: written as |str|

            .. seealso::
                :ref:`example-type-hint-python`
    """

    FORMAT_NAME = "python"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._dp_extractor.type_value_map = {
            typepy.Typecode.NONE: None,
            typepy.Typecode.INFINITY: 'float("inf")',
            typepy.Typecode.NAN: 'float("nan")',
        }

    def get_variable_name(self, value: str) -> str:
        return sanitize_python_var_name(self.table_name, "_").lower()

    def _write_table(self, **kwargs) -> None:
        if self.is_datetime_instance_formatting:
            self._dp_extractor.datetime_formatter = dateutil_datetime_formatter
        else:
            self._dp_extractor.datetime_formatter = quote_datetime_formatter

        self.inc_indent_level()
        super()._write_table(**kwargs)
        self.dec_indent_level()

    def _get_opening_row_items(self) -> List[str]:
        if typepy.is_not_null_string(self.table_name):
            return [self.variable_name + " = ["]

        return ["["]

    def _get_closing_row_items(self) -> List[str]:
        return ["]"]
