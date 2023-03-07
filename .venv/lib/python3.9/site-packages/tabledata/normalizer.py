"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import abc
import warnings
from typing import List, Sequence

import typepy

from ._core import TableData
from ._logger import logger
from .error import InvalidHeaderNameError, InvalidTableNameError


class TableDataNormalizerInterface(metaclass=abc.ABCMeta):
    """
    Interface class to validate and normalize data of |TableData|.
    """

    @abc.abstractmethod
    def validate(self) -> None:  # pragma: no cover
        pass

    @abc.abstractmethod
    def normalize(self) -> TableData:  # pragma: no cover
        pass


class AbstractTableDataNormalizer(TableDataNormalizerInterface):
    @property
    def _type_hints(self):
        return self._tabledata.dp_extractor.column_type_hints

    def __init__(self, tabledata: TableData) -> None:
        self._tabledata = tabledata

    def validate(self) -> None:
        if not self._tabledata.table_name:
            raise ValueError("table_name must not be empty")

        self._validate_table_name(self._tabledata.table_name)
        self._validate_headers()

    def sanitize(self):
        warnings.warn("'sanitize()' has moved to 'normalize()'", DeprecationWarning)

        return self.normalize()

    def normalize(self) -> TableData:
        """
        :return: Sanitized table data.
        :rtype: tabledata.TableData
        """

        logger.debug(f"normalize: {type(self).__name__}")

        normalize_headers = self._normalize_headers()

        return TableData(
            self.__normalize_table_name(),
            normalize_headers,
            self._normalize_rows(normalize_headers),
            dp_extractor=self._tabledata.dp_extractor,
            type_hints=self._type_hints,
            max_workers=self._tabledata.max_workers,
        )

    @abc.abstractmethod
    def _preprocess_table_name(self) -> str:
        """
        This method is always called before table name validation.
        You must return preprocessed table name.
        """

    @abc.abstractmethod
    def _validate_table_name(self, table_name: str) -> None:
        """
        Must raise :py:class:`~.InvalidTableNameError`
        when you consider the table name invalid.

        :param str header: Table name to validate.
        :raises tabledata.InvalidTableNameError:
            If the table name is invalid.
            |raises_validate_table_name|
        """

    @abc.abstractmethod
    def _normalize_table_name(self, table_name: str) -> str:
        """
        Must return a valid table name.
        The table name must be considered to be a valid name by
        :py:meth:`~._validate_table_name` method.

        This method called when :py:meth:`~._validate_table_name` method raise
        :py:class:`~.InvalidTableNameError`.

        :param str table_name: Table name to normalize.
        :return: Sanitized table name.
        :rtype: str
        """

    @abc.abstractmethod
    def _preprocess_header(self, col_idx: int, header: str) -> str:
        """
        This method is always called before a header validation.
        You must return preprocessed header.
        """

    @abc.abstractmethod
    def _validate_header(self, header: str) -> None:
        """
        No operation.

        This method called for each table header. Override this method
        in a subclass if you want to detect invalid table header elements.
        Raise :py:class:`~.InvalidHeaderNameError` if an invalid
        header element found.

        :param str header: Table header name.
        :raises tabledata.InvalidHeaderNameError:
            If the ``header`` is invalid.
        """

    @abc.abstractmethod
    def _normalize_header(self, header: str) -> str:
        """
        Must return a valid header name.
        This method called when :py:meth:`~._validate_header` method raise
        :py:class:`~.InvalidHeaderNameError`.
        Override this method in subclass if you want to rename invalid
        table header element.

        :param str header: Header name to normalize.
        :return: Renamed header name.
        :rtype: str
        """

    def _normalize_rows(self, normalize_headers: Sequence[str]) -> List:
        return self._tabledata.rows  # type: ignore

    def _validate_headers(self) -> None:
        for header in self._tabledata.headers:
            self._validate_header(header)

    def __normalize_table_name(self) -> str:
        preprocessed_table_name = self._preprocess_table_name()

        try:
            self._validate_table_name(preprocessed_table_name)
            new_table_name = preprocessed_table_name
        except InvalidTableNameError:
            new_table_name = self._normalize_table_name(preprocessed_table_name)
            self._validate_table_name(new_table_name)

        return new_table_name

    def _normalize_headers(self) -> List[str]:
        new_header_list = []

        for col_idx, header in enumerate(self._tabledata.headers):
            header = self._preprocess_header(col_idx, header)

            try:
                self._validate_header(header)
                new_header = header
            except InvalidHeaderNameError:
                new_header = self._normalize_header(header)
                self._validate_header(new_header)

            new_header_list.append(new_header)

        return new_header_list


class TableDataNormalizer(AbstractTableDataNormalizer):
    def _preprocess_table_name(self) -> str:
        if not self._tabledata.table_name:
            return ""

        return self._tabledata.table_name

    def _validate_table_name(self, table_name: str) -> None:
        try:
            typepy.String(table_name).validate()
        except TypeError as e:
            raise InvalidTableNameError(e)

    def _normalize_table_name(self, table_name: str) -> str:
        return typepy.String(table_name).force_convert()

    def _preprocess_header(self, col_idx: int, header: str) -> str:
        return header

    def _validate_header(self, header: str) -> None:
        try:
            typepy.String(header).validate()
        except TypeError as e:
            raise InvalidHeaderNameError(e)

    def _normalize_header(self, header: str) -> str:
        return typepy.String(header).force_convert()
