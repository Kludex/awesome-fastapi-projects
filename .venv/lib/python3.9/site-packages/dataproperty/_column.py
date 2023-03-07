from typing import List, Optional

from mbstrdecoder import MultiByteStrDecoder
from typepy import Integer, StrictLevel, Typecode, TypeConversionError

from ._align import Align
from ._align_getter import align_getter
from ._base import DataPeropertyBase
from ._common import DefaultValue
from ._container import ListContainer, MinMaxContainer
from ._dataproperty import DataProperty
from ._function import calc_ascii_char_width
from .typing import FloatType


class ColumnDataProperty(DataPeropertyBase):
    __slots__ = (
        "__header_ascii_char_width",
        "__body_ascii_char_width",
        "__column_index",
        "__dp_list",
        "__float_type",
        "__format_map",
        "__is_calculate",
        "__max_precision",
        "__minmax_integer_digits",
        "__minmax_decimal_places",
        "__minmax_additional_format_len",
        "__typecode_bitmap",
    )

    @property
    def align(self) -> Align:
        return align_getter.get_align_from_typecode(self.typecode)

    @property
    def bit_length(self) -> Optional[int]:
        if self.typecode != Typecode.INTEGER:
            return None

        bit_length = 0
        for value_dp in self.__dp_list:
            try:
                bit_length = max(bit_length, int.bit_length(value_dp.data))
            except TypeError:
                pass

        return bit_length

    @property
    def column_index(self) -> int:
        return self.__column_index

    @property
    def decimal_places(self) -> Optional[int]:
        return self._decimal_places

    @property
    def ascii_char_width(self) -> int:
        return max(self.__header_ascii_char_width, self.__body_ascii_char_width)

    @property
    def minmax_integer_digits(self) -> MinMaxContainer:
        return self.__minmax_integer_digits

    @property
    def minmax_decimal_places(self) -> ListContainer:
        return self.__minmax_decimal_places

    @property
    def minmax_additional_format_len(self) -> MinMaxContainer:
        return self.__minmax_additional_format_len

    def __init__(
        self,
        column_index: int,
        float_type: Optional[FloatType],
        min_width: int = 0,
        format_flags: Optional[int] = None,
        is_formatting_float: bool = True,
        datetime_format_str: str = DefaultValue.DATETIME_FORMAT,
        east_asian_ambiguous_width: int = 1,
        max_precision: int = DefaultValue.MAX_PRECISION,
    ) -> None:
        super().__init__(
            format_flags=format_flags,
            is_formatting_float=is_formatting_float,
            datetime_format_str=datetime_format_str,
            east_asian_ambiguous_width=east_asian_ambiguous_width,
        )

        self.__header_ascii_char_width = 0
        self.__body_ascii_char_width = min_width
        self.__column_index = column_index

        self.__float_type = float_type

        self.__is_calculate = True
        self.__dp_list: List[DataProperty] = []
        self.__minmax_integer_digits = MinMaxContainer()
        self.__minmax_decimal_places = ListContainer()
        self.__minmax_additional_format_len = MinMaxContainer()
        self.__max_precision = max_precision

        self.__typecode_bitmap = Typecode.NONE.value
        self.__calc_typecode_from_bitmap()

        self.__format_map = self._formatter.make_format_map(decimal_places=self._decimal_places)

    def __repr__(self) -> str:
        element_list = []

        if self.column_index is not None:
            element_list.append(f"column={self.column_index}")

        element_list.extend(
            [
                f"type={self.typename}",
                f"align={self.align.align_string}",
                f"ascii_width={self.ascii_char_width}",
            ]
        )

        if Integer(self.bit_length).is_type():
            element_list.append(f"bit_len={self.bit_length}")

        if self.minmax_integer_digits.has_value():
            if self.minmax_integer_digits.is_same_value():
                value = f"int_digits={self.minmax_integer_digits.min_value}"
            else:
                value = f"int_digits=({self.minmax_integer_digits})"

            element_list.append(value)

        if self.minmax_decimal_places.has_value():
            if self.minmax_decimal_places.is_same_value():
                value = f"decimal_places={self.minmax_decimal_places.min_value}"
            else:
                value = f"decimal_places=({self.minmax_decimal_places})"

            element_list.append(value)

        if not self.minmax_additional_format_len.is_zero():
            if self.minmax_additional_format_len.is_same_value():
                value = f"extra_len={self.minmax_additional_format_len.min_value}"
            else:
                value = f"extra_len=({self.minmax_additional_format_len})"

            element_list.append(value)

        return ", ".join(element_list)

    def dp_to_str(self, value_dp: DataProperty) -> str:
        if value_dp.typecode == Typecode.STRING:
            return value_dp.data

        try:
            value = self.__preprocess_value_before_tostring(value_dp)
        except TypeConversionError:
            return self.__format_map.get(value_dp.typecode, "{:s}").format(value_dp.data)

        to_string_format_str = self.__get_tostring_format(value_dp)

        try:
            return to_string_format_str.format(value)
        except (ValueError, TypeError):
            pass

        try:
            return MultiByteStrDecoder(value).unicode_str
        except ValueError:
            pass

        return str(value)

    def extend_width(self, ascii_char_width: int) -> None:
        self.extend_header_width(ascii_char_width)
        self.extend_body_width(ascii_char_width)

    def extend_header_width(self, ascii_char_width: int) -> None:
        self.__header_ascii_char_width += ascii_char_width

    def extend_body_width(self, ascii_char_width: int) -> None:
        self.__body_ascii_char_width += ascii_char_width

    def update_header(self, header_db: DataProperty) -> None:
        self.__header_ascii_char_width = header_db.ascii_char_width

    def update_body(self, value_dp: DataProperty) -> None:
        if value_dp.is_include_ansi_escape:
            value_dp = value_dp.no_ansi_escape_dp

        self.__typecode_bitmap |= value_dp.typecode.value
        self.__calc_typecode_from_bitmap()

        if value_dp.typecode in (Typecode.REAL_NUMBER, Typecode.INTEGER):
            self.__minmax_integer_digits.update(value_dp.integer_digits)
            self.__minmax_decimal_places.update(value_dp.decimal_places)
            self.__update_decimal_places()

        self.__minmax_additional_format_len.update(value_dp.additional_format_len)

        self.__dp_list.append(value_dp)
        self.__update_ascii_char_width()

    def merge(self, column_dp) -> None:
        self.__typecode_bitmap |= column_dp.typecode.value
        self.__calc_typecode_from_bitmap()

        self.__minmax_integer_digits.merge(column_dp.minmax_integer_digits)
        self.__minmax_decimal_places.update(column_dp.minmax_decimal_places)
        self.__update_decimal_places()

        self.__minmax_additional_format_len.merge(column_dp.minmax_additional_format_len)

        self.__body_ascii_char_width = max(self.__body_ascii_char_width, column_dp.ascii_char_width)
        self.__update_ascii_char_width()

    def begin_update(self) -> None:
        self.__is_calculate = False

    def end_update(self) -> None:
        self.__is_calculate = True

        self.__calc_typecode_from_bitmap()
        self.__update_decimal_places()
        self.__update_ascii_char_width()

    def __is_not_single_typecode(self, typecode_bitmap: int) -> bool:
        return bool(
            self.__typecode_bitmap & typecode_bitmap and self.__typecode_bitmap & ~typecode_bitmap
        )

    def __is_float_typecode(self) -> bool:
        FLOAT_TYPECODE_BMP = (
            Typecode.REAL_NUMBER.value | Typecode.INFINITY.value | Typecode.NAN.value
        )
        NUMBER_TYPECODE_BMP = FLOAT_TYPECODE_BMP | Typecode.INTEGER.value

        if self.__is_not_single_typecode(NUMBER_TYPECODE_BMP | Typecode.NULL_STRING.value):
            return False

        if (
            bin(self.__typecode_bitmap & (FLOAT_TYPECODE_BMP | Typecode.NULL_STRING.value)).count(
                "1"
            )
            >= 2
        ):
            return True

        if bin(self.__typecode_bitmap & NUMBER_TYPECODE_BMP).count("1") >= 2:
            return True

        return False

    def __calc_body_ascii_char_width(self) -> int:
        width_list = [self.__body_ascii_char_width]

        for value_dp in self.__dp_list:
            if value_dp.is_include_ansi_escape:
                value_dp = value_dp.no_ansi_escape_dp

            width_list.append(
                calc_ascii_char_width(self.dp_to_str(value_dp), self._east_asian_ambiguous_width)
            )

        return max(width_list)

    def __calc_decimal_places(self) -> Optional[int]:
        if self.minmax_decimal_places.max_value is None:
            return None

        return int(min(self.__max_precision, self.minmax_decimal_places.max_value))

    def __get_tostring_format(self, value_dp: DataProperty) -> str:
        if self.typecode == Typecode.STRING:
            return self.__format_map.get(value_dp.typecode, "{:s}")

        return self.__format_map.get(self.typecode, "{:s}")

    def __get_typecode_from_bitmap(self) -> Typecode:
        if self.__is_float_typecode():
            return Typecode.REAL_NUMBER

        if any(
            [
                self.__is_not_single_typecode(Typecode.BOOL.value),
                self.__is_not_single_typecode(Typecode.DATETIME.value),
            ]
        ):
            return Typecode.STRING

        typecode_list = [
            Typecode.STRING,
            Typecode.REAL_NUMBER,
            Typecode.INTEGER,
            Typecode.DATETIME,
            Typecode.DICTIONARY,
            Typecode.IP_ADDRESS,
            Typecode.LIST,
            Typecode.BOOL,
            Typecode.INFINITY,
            Typecode.NAN,
            Typecode.NULL_STRING,
        ]

        for typecode in typecode_list:
            if self.__typecode_bitmap & typecode.value:
                return typecode

        if self.__typecode_bitmap == Typecode.NONE.value:
            return Typecode.NONE

        return Typecode.STRING

    def __update_ascii_char_width(self) -> None:
        if not self.__is_calculate:
            return

        self.__body_ascii_char_width = self.__calc_body_ascii_char_width()

    def __update_decimal_places(self) -> None:
        if not self.__is_calculate:
            return

        self._decimal_places = self.__calc_decimal_places()
        self.__format_map = self._formatter.make_format_map(decimal_places=self._decimal_places)

    def __calc_typecode_from_bitmap(self) -> None:
        if not self.__is_calculate:
            return

        self._typecode = self.__get_typecode_from_bitmap()

    def __preprocess_value_before_tostring(self, value_dp: DataProperty):
        if self.typecode == value_dp.typecode or self.typecode in [
            Typecode.STRING,
            Typecode.BOOL,
            Typecode.DATETIME,
        ]:
            return value_dp.data

        return self.type_class(
            value_dp.data,
            strict_level=StrictLevel.MIN,
            float_type=self.__float_type,
            strip_ansi_escape=False,
        ).convert()
