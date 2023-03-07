from os.path import abspath

import tabledata

from ...error import EmptyValueError
from ._interface import AbstractBinaryTableWriter


class SqliteTableWriter(AbstractBinaryTableWriter):
    """
    A table writer class for `SQLite <https://www.sqlite.org/index.html>`__ database.

    .. py:method:: write_table()

        Write a table to a `SQLite <https://www.sqlite.org/index.html>`__ database.

        :raises pytablewriter.EmptyTableNameError:
            If the |table_name| is empty.
        :Example:
            :ref:`example-sqlite-table-writer`
    """

    FORMAT_NAME = "sqlite"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    def __init__(self, **kwargs) -> None:
        import copy

        import dataproperty

        super().__init__(**kwargs)

        self.is_padding = False
        self.is_formatting_float = False
        self._use_default_header = True

        self._is_require_table_name = True
        self._is_require_header = True

        self._quoting_flags = copy.deepcopy(dataproperty.NOT_QUOTING_FLAGS)

    def open(self, file_path: str) -> None:
        """
        Open a SQLite database file.

        :param str file_path: SQLite database file path to open.
        """

        from simplesqlite import SimpleSQLite

        if self.is_opened():
            if self.stream.database_path == abspath(file_path):
                self._logger.logger.debug(f"database already opened: {self.stream.database_path}")
                return

            self.close()

        self._stream = SimpleSQLite(file_path, "w", max_workers=self.max_workers)

    def dump(self, output: str, close_after_write: bool = True, **kwargs) -> None:
        """Write data to the SQLite database file.

        Args:
            output (file descriptor or filepath):
            close_after_write (bool, optional):
                Close the output after write.
                Defaults to |True|.
        """

        self.open(output)
        try:
            self.write_table(**kwargs)
        finally:
            if close_after_write:
                self.close()

    def _write_table(self, **kwargs) -> None:
        try:
            self._verify_value_matrix()
        except EmptyValueError:
            self._logger.logger.debug("no tabular data found")
            return

        self._preprocess()

        table_data = tabledata.TableData(
            self.table_name,
            self.headers,
            [
                [value_dp.data for value_dp in value_dp_list]
                for value_dp_list in self._table_value_dp_matrix
            ],
            type_hints=self.type_hints,
            max_workers=self.max_workers,
        )
        self.stream.create_table_from_tabledata(table_data)
