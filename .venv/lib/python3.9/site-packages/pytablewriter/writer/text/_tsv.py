from ._csv import CsvTableWriter


class TsvTableWriter(CsvTableWriter):
    """
    A table writer class for tab separated values (TSV) format.

        :Example:
            :ref:`example-tsv-table-writer`
    """

    FORMAT_NAME = "tsv"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.column_delimiter = "\t"
