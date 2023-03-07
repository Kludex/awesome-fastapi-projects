import pathvalidate
import typepy

from ._csv import CsvTableWriter


class LtsvTableWriter(CsvTableWriter):
    """
    A table writer class for
    `Labeled Tab-separated Values (LTSV) <http://ltsv.org/>`__ format.

        :Example:
            :ref:`example-ltsv-table-writer`
    """

    FORMAT_NAME = "ltsv"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.is_write_header = False

        self._is_require_header = True

    def write_table(self, **kwargs) -> None:
        """
        |write_table| with
        `Labeled Tab-separated Values (LTSV) <http://ltsv.org/>`__ format.
        Invalid characters in labels/data are removed.

        :Example:
            :ref:`example-ltsv-table-writer`
        """

        with self._logger:
            self._verify_property()
            self._preprocess()

            for values in self._table_value_matrix:
                ltsv_item_list = [
                    f"{pathvalidate.sanitize_ltsv_label(header_name):s}:{value}"
                    for header_name, value in zip(self.headers, values)
                    if typepy.is_not_null_string(value)
                ]

                if typepy.is_empty_sequence(ltsv_item_list):
                    continue

                self._write_line("\t".join(ltsv_item_list))
