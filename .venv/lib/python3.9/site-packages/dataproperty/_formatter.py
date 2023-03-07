import copy

from typepy import Nan, Typecode


class Format:
    NONE = 0
    THOUSAND_SEPARATOR = 1


class Formatter:
    __slots__ = ("__is_formatting_float", "__format_flags", "__datetime_format_str")

    _BLANK_CURLY_BRACES_FORMAT_MAP = {
        Typecode.NONE: "{}",
        Typecode.IP_ADDRESS: "{}",
        Typecode.BOOL: "{}",
        Typecode.DICTIONARY: "{}",
        Typecode.LIST: "{}",
    }

    def __init__(self, datetime_format_str, is_formatting_float=True, format_flags=None):
        if format_flags is not None:
            self.__format_flags = format_flags
        else:
            self.__format_flags = Format.NONE

        self.__datetime_format_str = datetime_format_str
        self.__is_formatting_float = is_formatting_float

    def make_format_map(self, decimal_places=None):
        format_map = copy.copy(self._BLANK_CURLY_BRACES_FORMAT_MAP)
        format_map.update(
            {
                Typecode.INTEGER: self.make_format_str(Typecode.INTEGER),
                Typecode.REAL_NUMBER: self.make_format_str(Typecode.REAL_NUMBER, decimal_places),
                Typecode.INFINITY: self.make_format_str(Typecode.INFINITY),
                Typecode.NAN: self.make_format_str(Typecode.NAN),
                Typecode.DATETIME: self.make_format_str(Typecode.DATETIME),
            }
        )

        return format_map

    def make_format_str(self, typecode, decimal_places=None):
        format_str = self._BLANK_CURLY_BRACES_FORMAT_MAP.get(typecode)
        if format_str is not None:
            return format_str

        if typecode == Typecode.INTEGER:
            return self.__get_integer_format()

        if typecode in (Typecode.REAL_NUMBER, Typecode.INFINITY, Typecode.NAN):
            return self.__get_realnumber_format(decimal_places)

        if typecode == Typecode.DATETIME:
            return "{:" + self.__datetime_format_str + "}"

        return "{:s}"

    def __get_base_format_str(self):
        if self.__format_flags & Format.THOUSAND_SEPARATOR:
            return ","

        return ""

    def __get_integer_format(self):
        return "{:" + self.__get_base_format_str() + "d}"

    def __get_realnumber_format(self, decimal_places):
        if not self.__is_formatting_float:
            return "{}"

        base_format = self.__get_base_format_str()

        if decimal_places is None or Nan(decimal_places).is_type():
            return "{:" + base_format + "f}"

        try:
            return "{:" + f"{base_format:s}.{decimal_places:d}f" + "}"
        except ValueError:
            pass

        return "{:" + base_format + "f}"
