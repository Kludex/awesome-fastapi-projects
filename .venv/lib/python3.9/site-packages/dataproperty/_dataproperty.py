"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from decimal import Decimal
from typing import Any, Optional, cast

from mbstrdecoder import MultiByteStrDecoder
from typepy import (
    Bool,
    DateTime,
    Dictionary,
    Infinity,
    Integer,
    IpAddress,
    List,
    Nan,
    NoneType,
    NullString,
    RealNumber,
    StrictLevel,
    String,
    Typecode,
    TypeConversionError,
)

from ._align import Align
from ._align_getter import align_getter
from ._base import DataPeropertyBase
from ._common import DefaultValue
from ._function import calc_ascii_char_width, get_number_of_digit
from ._preprocessor import Preprocessor
from .typing import FloatType, StrictLevelMap, TypeHint


class DataProperty(DataPeropertyBase):
    __slots__ = (
        "__data",
        "__no_ansi_escape_data",
        "__align",
        "__integer_digits",
        "__additional_format_len",
        "__length",
        "__ascii_char_width",
    )

    __type_class_list = [
        NoneType,
        Integer,
        Infinity,
        Nan,
        IpAddress,
        RealNumber,
        Bool,
        List,
        Dictionary,
        DateTime,
        NullString,
        String,
    ]

    def __init__(
        self,
        data: Any,
        preprocessor: Optional[Preprocessor] = None,
        type_hint: TypeHint = None,
        float_type: Optional[FloatType] = None,
        format_flags: Optional[int] = None,
        datetime_format_str: str = DefaultValue.DATETIME_FORMAT,
        strict_level_map: Optional[StrictLevelMap] = None,
        east_asian_ambiguous_width: int = 1,
    ) -> None:
        super().__init__(
            format_flags=format_flags,
            is_formatting_float=True,
            datetime_format_str=datetime_format_str,
            east_asian_ambiguous_width=east_asian_ambiguous_width,
        )

        self.__additional_format_len: Optional[int] = None
        self.__align: Optional[Align] = None
        self.__ascii_char_width: Optional[int] = None
        self.__integer_digits: Optional[int] = None
        self.__length: Optional[int] = None

        if preprocessor is None:
            preprocessor = Preprocessor()

        data, no_ansi_escape_data = preprocessor.preprocess(data)

        self.__set_data(data, type_hint, float_type, strict_level_map)

        if no_ansi_escape_data is None or len(data) == len(no_ansi_escape_data):
            self.__no_ansi_escape_data: Optional[DataProperty] = None
        else:
            self.__no_ansi_escape_data = DataProperty(no_ansi_escape_data, float_type=float_type)

    def __eq__(self, other) -> bool:
        if self.typecode != other.typecode:
            return False

        if self.typecode == Typecode.NAN:
            return True

        return self.data == other.data

    def __ne__(self, other) -> bool:
        if self.typecode != other.typecode:
            return True

        if self.typecode == Typecode.NAN:
            return False

        return self.data != other.data

    def __repr__(self) -> str:
        element_list = []

        if self.typecode == Typecode.DATETIME:
            element_list.append(f"data={str(self.data):s}")
        else:
            try:
                element_list.append("data=" + self.to_str())
            except UnicodeEncodeError:
                element_list.append(f"data={MultiByteStrDecoder(self.data).unicode_str}")

        element_list.extend(
            [
                f"type={self.typename:s}",
                f"align={self.align.align_string}",
                f"ascii_width={self.ascii_char_width:d}",
            ]
        )

        if Integer(self.length).is_type():
            element_list.append(f"length={self.length}")

        if Integer(self.integer_digits).is_type():
            element_list.append(f"int_digits={self.integer_digits}")

        if Integer(self.decimal_places).is_type():
            element_list.append(f"decimal_places={self.decimal_places}")

        if Integer(self.additional_format_len).is_type():
            element_list.append(f"extra_len={self.additional_format_len}")

        return ", ".join(element_list)

    @property
    def align(self) -> Align:
        if not self.__align:
            if self.is_include_ansi_escape:
                self.__align = self.no_ansi_escape_dp.align
            else:
                self.__align = align_getter.get_align_from_typecode(self.typecode)

        assert self.__align

        return self.__align

    @property
    def decimal_places(self) -> Optional[int]:
        """
        :return:
            Decimal places if the ``data`` type either ``float`` or
            ``decimal.Decimal``. Returns ``0`` if the ``data`` type is ``int``.
            Otherwise, returns ``float("nan")``.
        :rtype: int
        """

        if self._decimal_places is None:
            self.__set_digit()

        return self._decimal_places

    @property
    def data(self) -> Any:
        """
        :return: Original data value.
        :rtype: Original data type.
        """

        return self.__data

    @property
    def is_include_ansi_escape(self) -> bool:
        if self.no_ansi_escape_dp is None:
            return False

        return self.length != self.no_ansi_escape_dp.length

    @property
    def no_ansi_escape_dp(self):
        return self.__no_ansi_escape_data

    @property
    def length(self) -> Optional[int]:
        """
        :return: Length of the ``data``.
        :rtype: int
        """

        if self.__length is None:
            self.__length = self.__get_length()

        return self.__length

    @property
    def ascii_char_width(self) -> int:
        if self.__ascii_char_width is None:
            self.__ascii_char_width = self.__calc_ascii_char_width()

        return self.__ascii_char_width

    @property
    def integer_digits(self) -> Optional[int]:
        """
        :return:
            Integer digits if the ``data`` type either
            ``int``/``float``/``decimal.Decimal``.
            Otherwise, returns ``None``.
        :rtype: int
        """

        if self.__integer_digits is None:
            self.__set_digit()

        return self.__integer_digits

    @property
    def additional_format_len(self) -> int:
        if self.__additional_format_len is None:
            self.__additional_format_len = self.__get_additional_format_len()

        return self.__additional_format_len

    def get_padding_len(self, ascii_char_width: int) -> int:
        if self.typecode in (Typecode.LIST, Typecode.DICTIONARY):
            unicode_str_len = DataProperty(MultiByteStrDecoder(str(self.data)).unicode_str).length
            assert unicode_str_len
            return max(
                ascii_char_width - (self.ascii_char_width - unicode_str_len),
                0,
            )

        try:
            return max(ascii_char_width - (self.ascii_char_width - cast(int, self.length)), 0)
        except TypeError:
            return ascii_char_width

    def to_str(self) -> str:
        return self.format_str.format(self.data)

    def __get_additional_format_len(self) -> int:
        if not RealNumber(self.data, strip_ansi_escape=False).is_type():
            return 0

        format_len = 0

        if Decimal(self.data) < 0:
            # for minus character
            format_len += 1

        return format_len

    def __get_base_float_len(self):
        assert self.integer_digits is not None
        assert self.decimal_places is not None

        if any([self.integer_digits < 0, self.decimal_places < 0]):
            raise ValueError("integer digits and decimal places must be greater or equals to zero")

        float_len = self.integer_digits + self.decimal_places
        if self.decimal_places > 0:
            # for dot
            float_len += 1

        return float_len

    def __get_length(self) -> Optional[int]:
        if self.typecode in (Typecode.DICTIONARY, Typecode.LIST, Typecode.STRING):
            return len(self.data)

        return None

    def __calc_ascii_char_width(self) -> int:
        if self.typecode == Typecode.INTEGER:
            return cast(int, self.integer_digits) + self.additional_format_len

        if self.typecode == Typecode.REAL_NUMBER:
            return self.__get_base_float_len() + self.additional_format_len

        if self.typecode == Typecode.DATETIME:
            try:
                return len(self.to_str())
            except ValueError:
                # reach to this line if the year <1900.
                # the datetime strftime() methods require year >= 1900.
                return len(str(self.data))

        if self.is_include_ansi_escape:
            return self.no_ansi_escape_dp.ascii_char_width

        try:
            unicode_str = MultiByteStrDecoder(self.data).unicode_str
        except ValueError:
            unicode_str = self.to_str()

        return calc_ascii_char_width(unicode_str, self._east_asian_ambiguous_width)

    def __set_data(
        self,
        data: Any,
        type_hint: TypeHint,
        float_type: Optional[FloatType],
        strict_level_map: Optional[StrictLevelMap],
    ):
        if float_type is None:
            float_type = DefaultValue.FLOAT_TYPE

        if strict_level_map is None:
            strict_level_map = DefaultValue.STRICT_LEVEL_MAP

        if type_hint:
            type_obj = type_hint(
                data, strict_level=StrictLevel.MIN, float_type=float_type, strip_ansi_escape=False
            )
            self._typecode = type_obj.typecode
            self.__data = type_obj.try_convert()

            if type_hint(
                self.__data,
                strict_level=StrictLevel.MAX,
                float_type=float_type,
                strip_ansi_escape=False,
            ).is_type():
                return

        for type_class in self.__type_class_list:
            strict_level = strict_level_map.get(
                type_class(None).typecode, strict_level_map.get("default", StrictLevel.MAX)
            )

            if self.__try_convert_type(data, type_class, strict_level, float_type):
                return

        raise TypeConversionError(
            f"failed to convert: data={data}, strict_level={strict_level_map}"
        )

    def __set_digit(self) -> None:
        integer_digits, decimal_places = get_number_of_digit(self.__data)
        self.__integer_digits = integer_digits
        self._decimal_places = decimal_places

    def __try_convert_type(self, data, type_class, strict_level, float_type):
        type_obj = type_class(data, strict_level, float_type=float_type, strip_ansi_escape=False)

        try:
            self.__data = type_obj.convert()
        except TypeConversionError:
            return False

        self._typecode = type_obj.typecode

        return True
