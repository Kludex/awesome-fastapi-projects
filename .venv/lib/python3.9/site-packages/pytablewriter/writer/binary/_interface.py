import abc

from .._table_writer import AbstractTableWriter


class BinaryWriterInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def is_opened(self) -> bool:  # pragma: no cover
        pass

    @abc.abstractmethod
    def open(self, file_path: str) -> None:  # pragma: no cover
        """
        Open a file for output stream.

        Args:
            file_path (str): path to the file.
        """


class AbstractBinaryTableWriter(AbstractTableWriter, BinaryWriterInterface):
    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, value) -> None:
        raise RuntimeError(
            "cannot assign a stream to binary format writers. use open method instead."
        )

    @property
    def support_split_write(self) -> bool:
        return True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.table_name = kwargs.get("table_name", "")

        self._stream = None

    def __del__(self) -> None:
        self.close()

    def is_opened(self) -> bool:
        return self.stream is not None

    def dumps(self) -> str:
        raise NotImplementedError("binary format writers did not support dumps method")

    def _verify_stream(self) -> None:
        if self.stream is None:
            raise OSError("null output stream. required to open(file_path) first.")

    def _write_value_row_separator(self) -> None:
        pass
