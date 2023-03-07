"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import copy
import enum
import sys
import typing
from collections import Counter
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple, Type, Union, cast

import typepy
from typepy import (
    Bool,
    DateTime,
    Dictionary,
    Infinity,
    Integer,
    IpAddress,
    Nan,
    NoneType,
    NullString,
    RealNumber,
    StrictLevel,
    String,
    Typecode,
    is_empty_sequence,
)
from typepy.type import AbstractType

from ._column import ColumnDataProperty
from ._common import MIN_STRICT_LEVEL_MAP, DefaultValue
from ._converter import DataPropertyConverter
from ._dataproperty import DataProperty
from ._formatter import Format
from ._preprocessor import Preprocessor
from .logger import logger
from .typing import StrictLevelMap, TransFunc, TypeHint, normalize_type_hint


@enum.unique
class MatrixFormatting(enum.Enum):
    # raise exception if the matrix is not properly formatted
    EXCEPTION = 1 << 1

    # trim to the minimum size column
    TRIM = 1 << 2

    # Append None values to columns so that it is the same as the maximum
    # column size.
    FILL_NONE = 1 << 3

    HEADER_ALIGNED = 1 << 4


class DataPropertyExtractor:
    """
    .. py:attribute:: quoting_flags

        Configurations to add double quote to for each items in a matrix,
        where |Typecode| of table-value is |True| in the ``quote_flag_table``
        mapping table. ``quote_flag_table`` should be a dictionary.
        And is ``{ Typecode : bool }``. Defaults to:

        .. code-block:: json
            :caption: The default values

            {
                Typecode.BOOL: False,
                Typecode.DATETIME: False,
                Typecode.DICTIONARY: False,
                Typecode.INFINITY: False,
                Typecode.INTEGER: False,
                Typecode.IP_ADDRESS: False,
                Typecode.LIST: False,
                Typecode.NAN: False,
                Typecode.NULL_STRING: False,
                Typecode.NONE: False,
                Typecode.REAL_NUMBER: False,
                Typecode.STRING: False,
            }
    """

    def __init__(self, max_precision: Optional[int] = None) -> None:
        self.max_workers = DefaultValue.MAX_WORKERS

        if max_precision is None:
            self.__max_precision = DefaultValue.MAX_PRECISION
        else:
            self.__max_precision = max_precision

        self.__headers: Sequence[str] = []
        self.__default_type_hint: TypeHint = None
        self.__col_type_hints: List[TypeHint] = []

        self.__strip_str_header: Optional[str] = None
        self.__is_formatting_float = True
        self.__min_col_ascii_char_width = 0
        self.__default_format_flags = Format.NONE
        self.__format_flags_list: Sequence[int] = []
        self.__float_type: Union[Type[float], Type[Decimal], None] = None
        self.__datetime_format_str = DefaultValue.DATETIME_FORMAT
        self.__strict_level_map = copy.deepcopy(
            cast(Dict[Union[Typecode, str], int], DefaultValue.STRICT_LEVEL_MAP)
        )
        self.__east_asian_ambiguous_width = 1

        self.__preprocessor = Preprocessor()

        self.__type_value_map: Mapping[Typecode, Union[float, Decimal, None]] = copy.deepcopy(
            DefaultValue.TYPE_VALUE_MAP
        )

        self.__trans_func_list: List[TransFunc] = []
        self.__quoting_flags = copy.deepcopy(DefaultValue.QUOTING_FLAGS)
        self.__datetime_formatter: Optional[Callable[[datetime], str]] = None
        self.__matrix_formatting = MatrixFormatting.TRIM

        self.__clear_cache()

    def __clear_cache(self) -> None:
        self.__update_dp_converter()
        self.__dp_cache_zero = self.__to_dp_raw(0)
        self.__dp_cache_one = self.__to_dp_raw(1)
        self.__dp_cache_true = self.__to_dp_raw(True)
        self.__dp_cache_false = self.__to_dp_raw(False)
        self.__dp_cache_map = {None: self.__to_dp_raw(None), "": self.__to_dp_raw("")}

    @property
    def headers(self) -> Sequence[str]:
        return self.__headers

    @headers.setter
    def headers(self, value: Sequence[str]) -> None:
        if self.__headers == value:
            return

        self.__headers = value
        self.__clear_cache()

    @property
    def default_type_hint(self) -> TypeHint:
        return self.__default_type_hint

    @default_type_hint.setter
    def default_type_hint(self, value: TypeHint) -> None:
        if self.__default_type_hint == value:
            return

        self.__default_type_hint = value
        self.__clear_cache()

    @property
    def column_type_hints(self) -> List[TypeHint]:
        return self.__col_type_hints

    @column_type_hints.setter
    def column_type_hints(self, value: Sequence[Union[str, TypeHint]]) -> None:
        normalized_type_hints: List[TypeHint] = []

        for type_hint in value:
            type_hint = normalize_type_hint(type_hint)
            if type_hint not in (
                Bool,
                DateTime,
                Dictionary,
                Infinity,
                Integer,
                IpAddress,
                typepy.List,
                Nan,
                NoneType,
                RealNumber,
                String,
                NullString,
                None,
            ):
                raise ValueError(f"invalid type hint: {type(type_hint)}")

            normalized_type_hints.append(type_hint)

        if self.__col_type_hints == normalized_type_hints:
            return

        self.__col_type_hints = normalized_type_hints
        self.__clear_cache()

    @property
    def is_formatting_float(self) -> bool:
        return self.__is_formatting_float

    @is_formatting_float.setter
    def is_formatting_float(self, value: bool) -> None:
        self.__is_formatting_float = value

    @property
    def max_precision(self) -> int:
        return self.__max_precision

    @max_precision.setter
    def max_precision(self, value: int) -> None:
        if self.__max_precision == value:
            return

        self.__max_precision = value
        self.__clear_cache()

    @property
    def preprocessor(self) -> Preprocessor:
        return self.__preprocessor

    @preprocessor.setter
    def preprocessor(self, value: Preprocessor) -> None:
        if self.preprocessor == value:
            return

        self.__preprocessor = value
        self.__update_dp_converter()

    @property
    def strip_str_header(self) -> Optional[str]:
        return self.__strip_str_header

    @strip_str_header.setter
    def strip_str_header(self, value: str):
        if self.__strip_str_header == value:
            return

        self.__strip_str_header = value
        self.__clear_cache()

    @property
    def min_column_width(self) -> int:
        return self.__min_col_ascii_char_width

    @min_column_width.setter
    def min_column_width(self, value: int):
        if self.__min_col_ascii_char_width == value:
            return

        self.__min_col_ascii_char_width = value
        self.__clear_cache()

    @property
    def default_format_flags(self) -> int:
        return self.__default_format_flags

    @default_format_flags.setter
    def default_format_flags(self, value: int):
        if self.__default_format_flags == value:
            return

        self.__default_format_flags = value
        self.__clear_cache()

    @property
    def format_flags_list(self) -> Sequence[int]:
        return self.__format_flags_list

    @format_flags_list.setter
    def format_flags_list(self, value: Sequence[int]):
        if self.__format_flags_list == value:
            return

        self.__format_flags_list = value
        self.__clear_cache()

    @property
    def float_type(self) -> Union[Type[float], Type[Decimal], None]:
        return self.__float_type

    @float_type.setter
    def float_type(self, value: Union[Type[float], Type[Decimal]]):
        if self.__float_type == value:
            return

        self.__float_type = value
        """
        self.__type_value_map = {
            Typecode.NONE: None,
            Typecode.INFINITY: self.__float_type("inf"),
            Typecode.NAN: self.__float_type("nan"),
        }
        """

        self.__clear_cache()

    @property
    def datetime_format_str(self) -> str:
        return self.__datetime_format_str

    @datetime_format_str.setter
    def datetime_format_str(self, value: str) -> None:
        if self.__datetime_format_str == value:
            return

        self.__datetime_format_str = value
        self.__clear_cache()

    @property
    def strict_level_map(self) -> StrictLevelMap:
        return self.__strict_level_map

    @strict_level_map.setter
    def strict_level_map(self, value: StrictLevelMap):
        if self.__strict_level_map == value:
            return

        self.__strict_level_map = cast(Dict[Union[Typecode, str], int], value)
        self.__clear_cache()

    @property
    def east_asian_ambiguous_width(self) -> int:
        return self.__east_asian_ambiguous_width

    @east_asian_ambiguous_width.setter
    def east_asian_ambiguous_width(self, value: int):
        if self.__east_asian_ambiguous_width == value:
            return

        self.__east_asian_ambiguous_width = value
        self.__clear_cache()

    @property
    def type_value_map(self):
        return self.__type_value_map

    @type_value_map.setter
    def type_value_map(self, value):
        if self.__type_value_map == value:
            return

        self.__type_value_map = value
        self.__clear_cache()

    def register_trans_func(self, trans_func: TransFunc) -> None:
        self.__trans_func_list.insert(0, trans_func)
        self.__clear_cache()

    @property
    def quoting_flags(self):
        return self.__quoting_flags

    @quoting_flags.setter
    def quoting_flags(self, value):
        if self.__quoting_flags == value:
            return

        self.__quoting_flags = value
        self.__clear_cache()

    @property
    def datetime_formatter(self) -> Optional[Callable[[datetime], str]]:
        return self.__datetime_formatter

    @datetime_formatter.setter
    def datetime_formatter(self, value: Callable[[datetime], str]) -> None:
        if self.__datetime_formatter == value:
            return

        self.__datetime_formatter = value
        self.__clear_cache()

    @property
    def matrix_formatting(self) -> MatrixFormatting:
        return self.__matrix_formatting

    @matrix_formatting.setter
    def matrix_formatting(self, value: MatrixFormatting):
        if self.__matrix_formatting == value:
            return

        self.__matrix_formatting = value
        self.__clear_cache()

    @property
    def max_workers(self) -> int:
        assert self.__max_workers

        return self.__max_workers

    @max_workers.setter
    def max_workers(self, value: Optional[int]):
        try:
            from _multiprocessing import SemLock, sem_unlink  # noqa
        except ImportError:
            logger.debug("This platform lacks a functioning sem_open implementation")
            value = 1

        if "pytest" in sys.modules and value != 1:
            logger.debug("set max_workers to 1 to avoid deadlock when executed from pytest")
            value = 1

        self.__max_workers = value
        if not self.__max_workers:
            self.__max_workers = DefaultValue.MAX_WORKERS

    def to_dp(self, value) -> DataProperty:
        self.__update_dp_converter()

        return self.__to_dp(value)

    def to_dp_list(self, values: Sequence) -> List[DataProperty]:
        if is_empty_sequence(values):
            return []

        self.__update_dp_converter()

        return self._to_dp_list(values)

    def to_column_dp_list(
        self,
        value_dp_matrix: Any,
        previous_column_dp_list: Optional[Sequence[ColumnDataProperty]] = None,
    ) -> List[ColumnDataProperty]:
        col_dp_list = self.__get_col_dp_list_base()

        logger.debug("converting to column dataproperty:")

        logs = ["  params:"]
        if self.headers:
            logs.append(f"    headers={len(self.headers)}")
        logs.extend(
            [
                "    prev_col_count={}".format(
                    len(previous_column_dp_list) if previous_column_dp_list else None
                ),
                f"    matrix_formatting={self.matrix_formatting}",
            ]
        )
        if self.column_type_hints:
            logs.append(
                "    column_type_hints=({})".format(
                    ", ".join(
                        [
                            type_hint.__name__ if type_hint else "none"
                            for type_hint in self.column_type_hints
                        ]
                    )
                )
            )
        else:
            logs.append("    column_type_hints=()")

        for log in logs:
            logger.debug(log)

        logger.debug("  results:")
        for col_idx, value_dp_list in enumerate(zip(*value_dp_matrix)):
            try:
                col_dp_list[col_idx]
            except IndexError:
                col_dp_list.append(
                    ColumnDataProperty(
                        column_index=col_idx,
                        float_type=self.float_type,
                        min_width=self.min_column_width,
                        format_flags=self.__get_format_flags(col_idx),
                        is_formatting_float=self.is_formatting_float,
                        datetime_format_str=self.datetime_format_str,
                        east_asian_ambiguous_width=self.east_asian_ambiguous_width,
                        max_precision=self.__max_precision,
                    )
                )

            col_dp = col_dp_list[col_idx]
            col_dp.begin_update()

            try:
                col_dp.merge(previous_column_dp_list[col_idx])  # type: ignore
            except (TypeError, IndexError):
                pass

            for value_dp in value_dp_list:
                col_dp.update_body(value_dp)

            col_dp.end_update()

            logger.debug(f"    {str(col_dp):s}")

        return col_dp_list

    def to_dp_matrix(self, value_matrix: Sequence) -> Sequence[Sequence[DataProperty]]:
        self.__update_dp_converter()
        logger.debug(f"max_workers={self.max_workers}, preprocessor={self.__preprocessor}")

        value_matrix = self.__strip_data_matrix(value_matrix)

        if self.__is_dp_matrix(value_matrix):
            logger.debug("already a dataproperty matrix")
            return value_matrix

        if self.max_workers <= 1:
            return self.__to_dp_matrix_st(value_matrix)

        return self.__to_dp_matrix_mt(value_matrix)

    def to_header_dp_list(self) -> List[DataProperty]:
        self.__update_dp_converter()

        preprocessor = copy.deepcopy(self.__preprocessor)
        preprocessor.strip_str = self.strip_str_header

        return self._to_dp_list(
            self.headers,
            type_hint=String,
            preprocessor=preprocessor,
            strict_level_map=MIN_STRICT_LEVEL_MAP,
        )

    def update_preprocessor(self, **kwargs) -> bool:
        is_updated = self.__preprocessor.update(**kwargs)
        self.__update_dp_converter()

        return is_updated

    def update_strict_level_map(self, value: StrictLevelMap) -> bool:
        org = copy.deepcopy(self.__strict_level_map)
        self.__strict_level_map.update(value)

        if org == self.__strict_level_map:
            return False

        self.__clear_cache()

        return True

    """
    def update_dict(self, lhs: Mapping, rhs: Mapping) -> bool:
        is_updated = False

        for key, value in rhs.items():
            if key not in lhs:
                lhs[]
                continue

            if getattr(lhs, key) == value:
                continue

            setattr(lhs, key, value)
            is_updated = True

        return is_updated
    """

    @staticmethod
    def __is_dp_matrix(value) -> bool:
        if not value:
            return False

        try:
            return isinstance(value[0][0], DataProperty)
        except (TypeError, IndexError):
            return False

    def __get_col_type_hint(self, col_idx: int) -> TypeHint:
        try:
            return self.column_type_hints[col_idx]
        except (TypeError, IndexError):
            return self.default_type_hint

    def __get_format_flags(self, col_idx: int):
        try:
            return self.format_flags_list[col_idx]
        except (TypeError, IndexError):
            return self.__default_format_flags

    def __to_dp(
        self,
        data,
        type_hint: TypeHint = None,
        preprocessor: Optional[Preprocessor] = None,
        strict_level_map: Optional[Dict] = None,
    ) -> DataProperty:
        for trans_func in self.__trans_func_list:
            data = trans_func(data)

        if type_hint:
            return self.__to_dp_raw(
                data,
                type_hint=type_hint,
                preprocessor=preprocessor,
                strict_level_map=strict_level_map,
            )

        try:
            if data in self.__dp_cache_map:
                return self.__dp_cache_map[data]
        except TypeError:
            # unhashable type
            pass

        if data == 0:
            if data is False:
                return self.__dp_cache_false
            return self.__dp_cache_zero
        if data == 1:
            if data is True:
                return self.__dp_cache_true
            return self.__dp_cache_one

        return self.__to_dp_raw(
            data, type_hint=type_hint, preprocessor=preprocessor, strict_level_map=strict_level_map
        )

    def __to_dp_raw(
        self,
        data,
        type_hint: TypeHint = None,
        preprocessor: Optional[Preprocessor] = None,
        strict_level_map: Optional[Dict] = None,
    ) -> DataProperty:
        if preprocessor:
            preprocessor = Preprocessor(
                dequote=preprocessor.dequote,
                line_break_handling=preprocessor.line_break_handling,
                line_break_repl=preprocessor.line_break_repl,
                strip_str=preprocessor.strip_str,
                is_escape_formula_injection=preprocessor.is_escape_formula_injection,
            )
        else:
            preprocessor = Preprocessor(
                dequote=self.preprocessor.dequote,
                line_break_handling=self.preprocessor.line_break_handling,
                line_break_repl=self.preprocessor.line_break_repl,
                strip_str=self.preprocessor.strip_str,
                is_escape_formula_injection=self.__preprocessor.is_escape_formula_injection,
            )

        value_dp = DataProperty(
            data,
            preprocessor=preprocessor,
            type_hint=(type_hint if type_hint is not None else self.default_type_hint),
            float_type=self.float_type,
            datetime_format_str=self.datetime_format_str,
            strict_level_map=(strict_level_map if type_hint is not None else self.strict_level_map),
            east_asian_ambiguous_width=self.east_asian_ambiguous_width,
        )

        return self.__dp_converter.convert(value_dp)

    def __to_dp_matrix_st(self, value_matrix) -> Sequence[Sequence[DataProperty]]:
        return list(
            zip(
                *(
                    _to_dp_list_helper(
                        self,
                        col_idx,
                        values,
                        self.__get_col_type_hint(col_idx),
                        self.__preprocessor,
                    )[1]
                    for col_idx, values in enumerate(zip(*value_matrix))
                )
            )
        )

    def __to_dp_matrix_mt(self, value_matrix) -> Sequence[Sequence[DataProperty]]:
        from concurrent import futures

        col_data_map = {}

        with futures.ProcessPoolExecutor(self.max_workers) as executor:
            future_list = [
                executor.submit(
                    _to_dp_list_helper,
                    self,
                    col_idx,
                    values,
                    self.__get_col_type_hint(col_idx),
                    self.__preprocessor,
                )
                for col_idx, values in enumerate(zip(*value_matrix))
            ]

            for future in futures.as_completed(future_list):
                col_idx, value_dp_list = future.result()
                col_data_map[col_idx] = value_dp_list

        return list(zip(*(col_data_map[col_idx] for col_idx in sorted(col_data_map))))

    def _to_dp_list(
        self,
        data_list: Sequence,
        type_hint: TypeHint = None,
        preprocessor: Optional[Preprocessor] = None,
        strict_level_map: Optional[Dict[Typecode, int]] = None,
    ) -> List[DataProperty]:
        if is_empty_sequence(data_list):
            return []

        type_counter: typing.Counter[Type[AbstractType]] = Counter()

        dp_list = []
        for data in data_list:
            expect_type_hint: TypeHint = type_hint
            if type_hint is None:
                try:
                    expect_type_hint, _count = type_counter.most_common(1)[0]
                    if not expect_type_hint(
                        data, float_type=self.float_type, strict_level=StrictLevel.MAX
                    ).is_type():
                        expect_type_hint = None
                except IndexError:
                    pass

            dataprop = self.__to_dp(
                data=data,
                type_hint=expect_type_hint,
                preprocessor=preprocessor if preprocessor else self.__preprocessor,
                strict_level_map=strict_level_map,
            )
            type_counter[dataprop.type_class] += 1

            dp_list.append(dataprop)

        return dp_list

    def __strip_data_matrix(self, data_matrix):
        header_col_size = len(self.headers) if self.headers else 0
        try:
            col_size_list = [len(data_list) for data_list in data_matrix]
        except TypeError:
            return []

        if self.headers:
            min_col_size = min([header_col_size] + col_size_list)
            max_col_size = max([header_col_size] + col_size_list)
        elif col_size_list:
            min_col_size = min(col_size_list)
            max_col_size = max(col_size_list)
        else:
            min_col_size = 0
            max_col_size = 0

        if self.matrix_formatting == MatrixFormatting.EXCEPTION:
            if min_col_size != max_col_size:
                raise ValueError(
                    "nonuniform column size found: min={}, max={}".format(
                        min_col_size, max_col_size
                    )
                )

            return data_matrix

        if self.matrix_formatting == MatrixFormatting.HEADER_ALIGNED:
            if header_col_size > 0:
                format_col_size = header_col_size
            else:
                format_col_size = max_col_size
        elif self.matrix_formatting == MatrixFormatting.TRIM:
            format_col_size = min_col_size
        elif self.matrix_formatting == MatrixFormatting.FILL_NONE:
            format_col_size = max_col_size
        else:
            raise ValueError(f"unknown matrix formatting: {self.matrix_formatting}")

        return [
            list(data_matrix[row_idx][:format_col_size]) + [None] * (format_col_size - col_size)
            for row_idx, col_size in enumerate(col_size_list)
        ]

    def __get_col_dp_list_base(self):
        header_dp_list = self.to_header_dp_list()
        col_dp_list = []

        for col_idx, header_dp in enumerate(header_dp_list):
            col_dp = ColumnDataProperty(
                column_index=col_idx,
                float_type=self.float_type,
                min_width=self.min_column_width,
                format_flags=self.__get_format_flags(col_idx),
                is_formatting_float=self.is_formatting_float,
                datetime_format_str=self.datetime_format_str,
                east_asian_ambiguous_width=self.east_asian_ambiguous_width,
                max_precision=self.__max_precision,
            )
            col_dp.update_header(header_dp)
            col_dp_list.append(col_dp)

        return col_dp_list

    def __update_dp_converter(self):
        preprocessor = Preprocessor(
            line_break_handling=self.__preprocessor.line_break_handling,
            line_break_repl=self.preprocessor.line_break_repl,
            is_escape_html_tag=self.__preprocessor.is_escape_html_tag,
            is_escape_formula_injection=self.__preprocessor.is_escape_formula_injection,
        )
        self.__dp_converter = DataPropertyConverter(
            preprocessor=preprocessor,
            type_value_map=self.type_value_map,
            quoting_flags=self.quoting_flags,
            datetime_formatter=self.datetime_formatter,
            datetime_format_str=self.datetime_format_str,
            float_type=self.float_type,
            strict_level_map=self.strict_level_map,
        )


def _to_dp_list_helper(
    extractor: DataPropertyExtractor,
    col_idx: int,
    data_list: Sequence,
    type_hint: TypeHint,
    preprocessor: Preprocessor,
) -> Tuple[int, List[DataProperty]]:
    return (
        col_idx,
        extractor._to_dp_list(data_list, type_hint=type_hint, preprocessor=preprocessor),
    )
