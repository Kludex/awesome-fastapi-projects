"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


from ._interface import TableWriterInterface
from .text._interface import IndentationInterface, TextWriterInterface


class NullTableWriter(IndentationInterface, TextWriterInterface, TableWriterInterface):
    FORMAT_NAME = "null"

    def __init__(self, **kwargs) -> None:
        self.table_name = kwargs.get("table_name", "")
        self.value_matrix = kwargs.get("value_matrix", [])
        self.is_formatting_float = kwargs.get("is_formatting_float", True)
        self.headers = kwargs.get("headers", [])
        self.type_hints = kwargs.get("type_hints", [])
        self.max_workers = kwargs.get("max_workers", 1)

    def __repr__(self) -> str:
        return self.dumps()

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return True

    def set_indent_level(self, indent_level: int) -> None:
        pass

    def inc_indent_level(self) -> None:
        pass

    def dec_indent_level(self) -> None:
        pass

    def write_null_line(self) -> None:
        pass

    def write_table(self, **kwargs) -> None:
        pass

    def dump(self, output, close_after_write: bool = True, **kwargs) -> None:
        pass

    def dumps(self) -> str:
        return ""

    def _write_table_iter(self, **kwargs) -> None:
        pass

    def close(self) -> None:
        pass

    def _write_value_row_separator(self) -> None:
        pass
