"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import abc


class TableWriterInterface(metaclass=abc.ABCMeta):
    """
    Interface class for writing a table.
    """

    @abc.abstractproperty
    def format_name(self) -> str:  # pragma: no cover
        """Format name for the writer.

        Returns:
            |str|
        """

    @abc.abstractproperty
    def support_split_write(self) -> bool:  # pragma: no cover
        """Represents the writer class supported iterative table writing
        (``write_table_iter`` method).

        Returns:
            bool: |True| if the writer supported iterative table writing.
        """

    @abc.abstractmethod
    def write_table(self, **kwargs) -> None:  # pragma: no cover
        """
        |write_table|.
        """

    def dump(self, output, close_after_write: bool, **kwargs) -> None:  # pragma: no cover
        raise NotImplementedError(f"{self.format_name} writer did not support dump method")

    def dumps(self) -> str:  # pragma: no cover
        raise NotImplementedError(f"{self.format_name} writer did not support dumps method")

    def write_table_iter(self, **kwargs) -> None:  # pragma: no cover
        """
        Write a table with iteration. "Iteration" means that divide the table
        writing into multiple processes.
        This method is useful, especially for large data.
        The following are premises to execute this method:

        - set iterator to the |value_matrix|
        - set the number of iterations to the |iteration_length| attribute

        Call back function (Optional):
        Callback function is called when for each of the iteration of writing
        a table is completed. To set call back function,
        set a callback function to the |write_callback| attribute.

        :raises pytablewriter.NotSupportedError:
            If the class does not support this method.

        .. note::
            Following classes do not support this method:
            |HtmlTableWriter|, |RstGridTableWriter|, |RstSimpleTableWriter|.
            ``support_split_write`` attribute return |True| if the class
            is supporting this method.
        """

        self._write_table_iter(**kwargs)

    @abc.abstractmethod
    def _write_table_iter(self, **kwargs) -> None:  # pragma: no cover
        pass

    @abc.abstractmethod
    def close(self) -> None:  # pragma: no cover
        pass

    @abc.abstractmethod
    def _write_value_row_separator(self) -> None:  # pragma: no cover
        pass
