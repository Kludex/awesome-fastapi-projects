from typing import Optional

import tabledata

from ...error import EmptyValueError
from ._interface import AbstractBinaryTableWriter


class PandasDataFramePickleWriter(AbstractBinaryTableWriter):
    """
    A table writer class for pandas DataFrame pickle.

    .. py:method:: write_table()

        Write a table to a pandas DataFrame pickle file.
    """

    FORMAT_NAME = "pandas_pickle"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return False

    def __init__(self, **kwargs) -> None:
        import copy

        import dataproperty

        super().__init__(**kwargs)

        self.is_padding = False
        self.is_formatting_float = False
        self._use_default_header = True

        self._quoting_flags = copy.deepcopy(dataproperty.NOT_QUOTING_FLAGS)

        self.__filepath: Optional[str] = None

    def is_opened(self) -> bool:
        return self.__filepath is not None

    def open(self, file_path: str) -> None:
        self.__filepath = file_path

    def close(self) -> None:
        super().close()
        self.__filepath = None

    def dump(self, output: str, close_after_write: bool = True, **kwargs) -> None:
        """Write data to a DataFrame pickle file.

        Args:
            output (file descriptor or filepath):
        """

        self.open(output)
        try:
            self.write_table(**kwargs)
        finally:
            if close_after_write:
                self.close()

    def _verify_stream(self) -> None:
        pass

    def _write_table(self, **kwargs) -> None:
        if not self.is_opened():
            self._logger.logger.error("required to open(file_path) first.")
            return

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
        table_data.as_dataframe().to_pickle(self.__filepath)

    def _write_table_iter(self, **kwargs) -> None:
        self._write_table(**kwargs)
