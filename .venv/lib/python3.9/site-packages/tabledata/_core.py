"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import copy
import re
from collections import OrderedDict, namedtuple
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple, Union

import dataproperty as dp
import typepy
from dataproperty.typing import TypeHint
from typepy import Nan

from ._constant import PatternMatch
from ._converter import to_value_matrix
from ._logger import logger


class TableData:
    """
    Class to represent a table data structure.

    :param table_name: Name of the table.
    :param  headers: Table header names.
    :param rows: Data of the table.
    """

    def __init__(
        self,
        table_name: Optional[str],
        headers: Sequence[str],
        rows: Sequence,
        dp_extractor: Optional[dp.DataPropertyExtractor] = None,
        type_hints: Optional[Sequence[Union[str, TypeHint]]] = None,
        max_workers: Optional[int] = None,
        max_precision: Optional[int] = None,
    ):
        self.__table_name = table_name
        self.__value_matrix: Optional[Sequence] = None
        self.__value_dp_matrix: Optional[Sequence[Sequence[dp.DataProperty]]] = None

        if rows:
            self.__rows = rows
        else:
            self.__rows = []

        if dp_extractor:
            self.__dp_extractor = copy.deepcopy(dp_extractor)
        else:
            self.__dp_extractor = dp.DataPropertyExtractor(max_precision=max_precision)

        if type_hints:
            self.__dp_extractor.column_type_hints = type_hints

        self.__dp_extractor.strip_str_header = '"'

        if max_workers:
            self.__dp_extractor.max_workers = max_workers

        if not headers:
            self.__dp_extractor.headers = []
        else:
            self.__dp_extractor.headers = headers

    def __repr__(self) -> str:
        element_list = [f"table_name={self.table_name}"]

        try:
            element_list.append("headers=[{}]".format(", ".join(self.headers)))
        except TypeError:
            element_list.append("headers=None")

        element_list.extend([f"cols={self.num_columns}", f"rows={self.num_rows}"])

        return ", ".join(element_list)

    def __eq__(self, other) -> bool:
        return self.equals(other, cmp_by_dp=False)

    def __ne__(self, other) -> bool:
        return not self.equals(other, cmp_by_dp=False)

    @property
    def table_name(self) -> Optional[str]:
        """
        :return: Name of the table.
        :rtype: str
        """

        return self.__table_name

    @table_name.setter
    def table_name(self, value: Optional[str]) -> None:
        self.__table_name = value

    @property
    def headers(self) -> Sequence[str]:
        """Get the table header names.

        Returns:
            |list| or |tuple|: Table header names.
        """

        return self.__dp_extractor.headers

    @property
    def rows(self) -> Sequence:
        """Original rows of tabular data.

        Returns:
            |list| or |tuple|: Table rows.
        """

        return self.__rows

    @property
    def value_matrix(self) -> Sequence:
        """Converted rows of tabular data.

        Returns:
            |list| or |tuple|: Table rows.
        """

        if self.__value_matrix:
            return self.__value_matrix

        self.__value_matrix = [
            [value_dp.data for value_dp in value_dp_list] for value_dp_list in self.value_dp_matrix
        ]

        return self.__value_matrix

    @property
    def has_value_dp_matrix(self) -> bool:
        return self.__value_dp_matrix is not None

    @property
    def max_workers(self) -> int:
        return self.__dp_extractor.max_workers

    @max_workers.setter
    def max_workers(self, value: Optional[int]) -> None:
        self.__dp_extractor.max_workers = value

    @property
    def num_rows(self) -> Optional[int]:
        """
        :return:
            Number of rows in the tabular data.
            |None| if the ``rows`` is neither list nor tuple.
        :rtype: int
        """

        try:
            return len(self.rows)
        except TypeError:
            return None

    @property
    def num_columns(self) -> Optional[int]:
        if typepy.is_not_empty_sequence(self.headers):
            return len(self.headers)

        try:
            return len(self.rows[0])
        except TypeError:
            return None
        except IndexError:
            return 0

    @property
    def value_dp_matrix(self) -> Sequence[Sequence[dp.DataProperty]]:
        """
        :return: DataProperty for table data.
        :rtype: list
        """

        if self.__value_dp_matrix is None:
            self.__value_dp_matrix = self.__dp_extractor.to_dp_matrix(
                to_value_matrix(self.headers, self.rows)
            )

        return self.__value_dp_matrix

    @property
    def header_dp_list(self) -> List[dp.DataProperty]:
        return self.__dp_extractor.to_header_dp_list()

    @property
    def column_dp_list(self) -> List[dp.ColumnDataProperty]:
        return self.__dp_extractor.to_column_dp_list(self.value_dp_matrix)

    @property
    def dp_extractor(self) -> dp.DataPropertyExtractor:
        return self.__dp_extractor

    def is_empty_header(self) -> bool:
        """
        :return: |True| if the data :py:attr:`.headers` is empty.
        :rtype: bool
        """

        return typepy.is_empty_sequence(self.headers)

    def is_empty_rows(self) -> bool:
        """
        :return: |True| if the tabular data has no rows.
        :rtype: bool
        """

        return self.num_rows == 0

    def is_empty(self) -> bool:
        """
        :return:
            |True| if the data :py:attr:`.headers` or
            :py:attr:`.value_matrix` is empty.
        :rtype: bool
        """

        return any([self.is_empty_header(), self.is_empty_rows()])

    def equals(self, other, cmp_by_dp: bool = True) -> bool:
        if cmp_by_dp:
            return self.__equals_dp(other)

        return self.__equals_raw(other)

    def __equals_base(self, other) -> bool:
        compare_item_list = [self.table_name == other.table_name]

        if self.num_rows is not None:
            compare_item_list.append(self.num_rows == other.num_rows)

        return all(compare_item_list)

    def __equals_raw(self, other) -> bool:
        if not self.__equals_base(other):
            return False

        if self.headers != other.headers:
            return False

        for lhs_row, rhs_row in zip(self.rows, other.rows):
            if len(lhs_row) != len(rhs_row):
                return False

            if not all(
                [
                    lhs == rhs
                    for lhs, rhs in zip(lhs_row, rhs_row)
                    if not Nan(lhs).is_type() and not Nan(rhs).is_type()
                ]
            ):
                return False

        return True

    def __equals_dp(self, other) -> bool:
        if not self.__equals_base(other):
            return False

        if self.header_dp_list != other.header_dp_list:
            return False

        if self.value_dp_matrix is None or other.value_dp_matrix is None:
            return False

        for lhs_list, rhs_list in zip(self.value_dp_matrix, other.value_dp_matrix):
            if len(lhs_list) != len(rhs_list):
                return False

            if any([lhs != rhs for lhs, rhs in zip(lhs_list, rhs_list)]):
                return False

        return True

    def in_tabledata_list(self, other: Sequence, cmp_by_dp: bool = True) -> bool:
        for table_data in other:
            if self.equals(table_data, cmp_by_dp=cmp_by_dp):
                return True

        return False

    def validate_rows(self) -> None:
        """
        :raises ValueError:
        """

        invalid_row_idx_list = []

        for row_idx, row in enumerate(self.rows):
            if isinstance(row, (list, tuple)) and len(self.headers) != len(row):
                invalid_row_idx_list.append(row_idx)

            if isinstance(row, dict):
                if not all([header in row for header in self.headers]):
                    invalid_row_idx_list.append(row_idx)

        if not invalid_row_idx_list:
            return

        for invalid_row_idx in invalid_row_idx_list:
            logger.debug(f"invalid row (line={invalid_row_idx}): {self.rows[invalid_row_idx]}")

        raise ValueError(
            "table header length and row length are mismatch:\n"
            + f"  header(len={len(self.headers)}): {self.headers}\n"
            + "  # of miss match rows: {} ouf of {}\n".format(
                len(invalid_row_idx_list), self.num_rows
            )
        )

    def as_dict(self, default_key: str = "table") -> Dict[str, List["OrderedDict[str, Any]"]]:
        """
        Args:
            default_key:
                Key of a returning dictionary when the ``table_name`` is empty.

        Returns:
            dict: Table data as a |dict| instance.

        Sample Code:
            .. code:: python

                from tabledata import TableData

                TableData(
                    "sample",
                    ["a", "b"],
                    [[1, 2], [3.3, 4.4]]
                ).as_dict()

        Output:
            .. code:: json

                {'sample': [OrderedDict([('a', 1), ('b', 2)]), OrderedDict([('a', 3.3), ('b', 4.4)])]}
        """  # noqa

        dict_body = []
        for row in self.value_matrix:
            if not row:
                continue

            values = [
                (header, value) for header, value in zip(self.headers, row) if value is not None
            ]

            if not values:
                continue

            dict_body.append(OrderedDict(values))

        table_name = self.table_name
        if not table_name:
            table_name = default_key

        return {table_name: dict_body}

    def as_tuple(self) -> Iterator[Tuple]:
        """
        :return: Rows of the tuple.
        :rtype: list of |namedtuple|

        :Sample Code:
            .. code:: python

                from tabledata import TableData

                records = TableData(
                    "sample",
                    ["a", "b"],
                    [[1, 2], [3.3, 4.4]]
                ).as_tuple()
                for record in records:
                    print(record)

        :Output:
            .. code-block:: none

                Row(a=1, b=2)
                Row(a=Decimal('3.3'), b=Decimal('4.4'))
        """

        Row = namedtuple("Row", self.headers)  # type: ignore

        for value_dp_list in self.value_dp_matrix:
            if typepy.is_empty_sequence(value_dp_list):
                continue

            row = Row(*(value_dp.data for value_dp in value_dp_list))

            yield row

    def as_dataframe(self):
        """
        :return: Table data as a ``pandas.DataFrame`` instance.
        :rtype: pandas.DataFrame

        :Sample Code:
            .. code-block:: python

                from tabledata import TableData

                TableData(
                    "sample",
                    ["a", "b"],
                    [[1, 2], [3.3, 4.4]]
                ).as_dataframe()

        :Output:
            .. code-block:: none

                     a    b
                0    1    2
                1  3.3  4.4

        :Dependency Packages:
            - `pandas <https://pandas.pydata.org/>`__
        """

        try:
            from pandas import DataFrame
        except ImportError:
            raise RuntimeError("required 'pandas' package to execute as_dataframe method")

        dataframe = DataFrame(self.value_matrix)
        if not self.is_empty_header():
            dataframe.columns = self.headers

        return dataframe

    def transpose(self) -> "TableData":
        return TableData(
            self.table_name,
            self.headers,
            [row for row in zip(*self.rows)],
            max_workers=self.max_workers,
        )

    def filter_column(
        self,
        patterns: Optional[str] = None,
        is_invert_match: bool = False,
        is_re_match: bool = False,
        pattern_match: PatternMatch = PatternMatch.OR,
    ) -> "TableData":
        logger.debug(
            "filter_column: patterns={}, is_invert_match={}, "
            "is_re_match={}, pattern_match={}".format(
                patterns, is_invert_match, is_re_match, pattern_match
            )
        )

        if not patterns:
            return self

        match_header_list = []
        match_column_matrix = []

        if pattern_match == PatternMatch.OR:
            match_method = any
        elif pattern_match == PatternMatch.AND:
            match_method = all
        else:
            raise ValueError(f"unknown matching: {pattern_match}")

        for header, column in zip(self.headers, zip(*self.rows)):
            is_match_list = []
            for pattern in patterns:
                is_match = self.__is_match(header, pattern, is_re_match)

                is_match_list.append(
                    any([is_match and not is_invert_match, not is_match and is_invert_match])
                )

            if match_method(is_match_list):
                match_header_list.append(header)
                match_column_matrix.append(column)

        logger.debug(
            "filter_column: table={}, match_header_list={}".format(
                self.table_name, match_header_list
            )
        )

        return TableData(
            self.table_name,
            match_header_list,
            list(zip(*match_column_matrix)),
            max_workers=self.max_workers,
        )

    @staticmethod
    def from_dataframe(
        dataframe,
        table_name: str = "",
        type_hints: Optional[Sequence[TypeHint]] = None,
        max_workers: Optional[int] = None,
    ) -> "TableData":
        """
        Initialize TableData instance from a pandas.DataFrame instance.

        :param pandas.DataFrame dataframe:
        :param str table_name: Table name to create.
        """

        return TableData(
            table_name,
            list(dataframe.columns.values),
            dataframe.values.tolist(),
            type_hints=type_hints,
            max_workers=max_workers,
        )

    @staticmethod
    def __is_match(header: str, pattern: str, is_re_match: bool) -> bool:
        if is_re_match:
            return re.search(pattern, header) is not None

        return header == pattern
