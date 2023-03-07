"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import copy
import re
from typing import List, Optional, Sequence

from ._func import to_codec_name


def b(s: str) -> bytes:
    return s.encode("latin-1")


class MultiByteStrDecoder:
    """
    Reference:
        https://docs.python.org/3/library/codecs.html
    """

    __CODECS = [
        "utf_7",
        "utf_8",
        "utf_8_sig",
        "utf_16",
        "utf_16_be",
        "utf_16_le",
        "utf_32",
        "utf_32_be",
        "utf_32_le",
        "big5",
        "big5hkscs",
        "cp037",
        "cp424",
        "cp437",
        "cp500",
        "cp720",
        "cp737",
        "cp775",
        "cp850",
        "cp852",
        "cp855",
        "cp856",
        "cp857",
        "cp858",
        "cp860",
        "cp861",
        "cp862",
        "cp863",
        "cp864",
        "cp865",
        "cp866",
        "cp869",
        "cp874",
        "cp875",
        "cp932",
        "cp949",
        "cp950",
        "cp1006",
        "cp1026",
        "cp1140",
        "cp1250",
        "cp1251",
        "cp1252",
        "cp1253",
        "cp1254",
        "cp1255",
        "cp1256",
        "cp1257",
        "cp1258",
        "euc_jp",
        "euc_jis_2004",
        "euc_jisx0213",
        "euc_kr",
        "gb2312",
        "gbk",
        "gb18030",
        "hz",
        "iso2022_jp",
        "iso2022_jp_1",
        "iso2022_jp_2",
        "iso2022_jp_2004",
        "iso2022_jp_3",
        "iso2022_jp_ext",
        "iso2022_kr",
        "latin_1",
        "iso8859_2",
        "iso8859_3",
        "iso8859_4",
        "iso8859_5",
        "iso8859_6",
        "iso8859_7",
        "iso8859_8",
        "iso8859_9",
        "iso8859_10",
        "iso8859_11",
        "iso8859_13",
        "iso8859_14",
        "iso8859_15",
        "iso8859_16",
        "johab",
        "koi8_r",
        "koi8_u",
        "mac_cyrillic",
        "mac_greek",
        "mac_iceland",
        "mac_latin2",
        "mac_roman",
        "mac_turkish",
        "ptcp154",
        "shift_jis",
        "shift_jis_2004",
        "shift_jisx0213",
        "base64_codec",
        "bz2_codec",
        "hex_codec",
        "idna",
        "mbcs",
        "palmos",
        "punycode",
        "quopri_codec",
        "raw_unicode_escape",
        "rot_13",
        "string_escape",
        "unicode_escape",
        "unicode_internal",
        "uu_codec",
        "zlib_codec",
    ]
    __RE_UTF7 = re.compile(b("[+].*?[-]"))

    @property
    def unicode_str(self) -> str:
        return self.__unicode_str

    @property
    def codec(self) -> Optional[str]:
        return self.__codec

    def __init__(self, value, codec_candidates: Optional[Sequence[str]] = None) -> None:
        self.__encoded_str = value
        self.__codec: Optional[str] = None
        if codec_candidates is None:
            self.__codec_candidate_list: List[str] = []
        else:
            self.__codec_candidate_list = list(codec_candidates)

        self.__validate_str()

        self.__unicode_str = self.__to_unicode()

    def __repr__(self) -> str:
        return f"codec={self.codec:s}, unicode={self.unicode_str:s}"

    def __validate_str(self) -> None:
        if isinstance(self.__encoded_str, (str, bytes)):
            return

        raise ValueError(f"value must be a string: actual={type(self.__encoded_str)}")

    def __is_buffer(self) -> bool:
        return isinstance(self.__encoded_str, memoryview)

    def __is_multibyte_utf7(self, encoded_str) -> bool:
        if self.__codec != "utf_7":
            return False

        utf7_symbol_count = encoded_str.count(b("+"))
        if utf7_symbol_count <= 0:
            return False

        if utf7_symbol_count != encoded_str.count(b("-")):
            return False

        return utf7_symbol_count == len(self.__RE_UTF7.findall(encoded_str))

    def __get_encoded_str(self) -> str:
        if self.__is_buffer():
            return str(self.__encoded_str)

        return self.__encoded_str

    @staticmethod
    def __detect_encoding_helper(encoded_str) -> Optional[str]:
        import chardet

        try:
            detect = chardet.detect(encoded_str)
        except TypeError:
            detect = {}  # type: ignore

        detect_encoding = detect.get("encoding")
        confidence = detect.get("confidence")

        if detect_encoding not in ["ascii", "utf-8"] and confidence and confidence > 0.7:
            # utf7 tend to be misrecognized as ascii
            return detect_encoding

        return None

    def __get_codec_candidate_list(self, encoded_str) -> List[str]:
        codec_candidate_list = copy.deepcopy(self.__CODECS)
        detect_encoding = self.__detect_encoding_helper(encoded_str)

        if detect_encoding:
            try:
                codec_candidate_list.remove(detect_encoding)
            except ValueError:
                pass

            codec_candidate_list.insert(0, detect_encoding)

        for codec_candidate in self.__codec_candidate_list:
            try:
                codec_candidate_list.remove(codec_candidate)
            except ValueError:
                pass

        return self.__codec_candidate_list + codec_candidate_list

    def __to_unicode(self):
        encoded_str = self.__get_encoded_str()

        if encoded_str == b"":
            self.__codec = "unicode"
            return ""

        for codec in self.__get_codec_candidate_list(encoded_str):
            if not codec:
                continue

            try:
                self.__codec = to_codec_name(codec)
                decoded_str = encoded_str.decode(codec)
                break
            except UnicodeDecodeError:
                self.__codec = None
                continue
            except AttributeError:
                if isinstance(encoded_str, str):
                    # already a unicode string (python 3)
                    self.__codec = "unicode"

                    if not encoded_str:
                        return encoded_str

                    return encoded_str

                self.__codec = None

                try:
                    return f"{encoded_str}"
                except UnicodeDecodeError:
                    # some of the objects that cannot convertible to a string
                    # may reach this line
                    raise TypeError("argument must be a string")
        else:
            self.__codec = None

            try:
                message = f"unknown codec: encoded_str={encoded_str}"
            except UnicodeDecodeError:
                message = f"unknown codec: value-type={type(encoded_str)}"

            raise UnicodeDecodeError(message)

        if self.codec == "utf_7":
            return self.__process_utf7(encoded_str, decoded_str)

        return decoded_str

    def __process_utf7(self, encoded_str, decoded_str) -> str:
        if not encoded_str:
            self.__codec = "unicode"

            return encoded_str

        if self.__is_multibyte_utf7(encoded_str):
            try:
                decoded_str.encode("ascii")

                self.__codec = "ascii"

                return encoded_str.decode("ascii")
            except UnicodeEncodeError:
                return decoded_str

        self.__codec = "ascii"

        return encoded_str.decode("ascii")
