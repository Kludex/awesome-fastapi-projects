import html
import re
from typing import Any, Optional, Tuple, Union

from mbstrdecoder import MultiByteStrDecoder

from ._function import strip_ansi_escape
from ._line_break import LineBreakHandling


_RE_LINE_BREAK = re.compile(r"\r\n|\n")
_RE_FORMULA_PREFIX = re.compile(r"^[-\+=@]")


def normalize_lbh(value: Optional[LineBreakHandling]) -> LineBreakHandling:
    if isinstance(value, LineBreakHandling):
        return value

    if value is None:
        return LineBreakHandling.NOP

    return LineBreakHandling[value.upper()]  # type: ignore


class Preprocessor:
    @property
    def line_break_handling(self) -> Optional[LineBreakHandling]:
        return self.__line_break_handling

    @line_break_handling.setter
    def line_break_handling(self, value: Optional[LineBreakHandling]):
        self.__line_break_handling = normalize_lbh(value)

    def __init__(
        self,
        strip_str: Optional[Union[str, bytes]] = None,
        replace_tabs_with_spaces: bool = True,
        tab_length: int = 2,
        line_break_handling: Optional[LineBreakHandling] = None,
        line_break_repl: str = " ",
        dequote: bool = False,
        is_escape_html_tag: bool = False,
        is_escape_formula_injection: bool = False,
    ) -> None:
        self.strip_str: Optional[Union[str, bytes]] = strip_str
        self.replace_tabs_with_spaces = replace_tabs_with_spaces
        self.tab_length = tab_length
        self.line_break_handling = line_break_handling
        self.line_break_repl = line_break_repl
        self.dequote = dequote
        self.is_escape_html_tag = is_escape_html_tag
        self.is_escape_formula_injection = is_escape_formula_injection

    def __repr__(self) -> str:
        return ", ".join(
            [
                f"strip_str={self.strip_str!r}",
                f"replace_tabs_with_spaces={self.replace_tabs_with_spaces}",
                f"tab_length={self.tab_length}",
                f"line_break_handling={self.line_break_handling}",
                f"line_break_repl={self.line_break_repl}",
                f"escape_html_tag={self.is_escape_html_tag}",
                f"escape_formula_injection={self.is_escape_formula_injection}",
            ]
        )

    def preprocess(self, data: Any) -> Tuple:
        data, no_ansi_escape_data = self.__preprocess_string(
            self.__preprocess_data(data, self.strip_str),
        )
        return (data, no_ansi_escape_data)

    def update(self, **kwargs) -> bool:
        is_updated = False

        for key, value in kwargs.items():
            if not hasattr(self, key):
                continue

            if getattr(self, key) == value:
                continue

            setattr(self, key, value)
            is_updated = True

        return is_updated

    def __preprocess_string(self, raw_data):
        data = raw_data

        if not isinstance(data, str):
            return (data, None)

        if self.replace_tabs_with_spaces:
            try:
                data = data.replace("\t", " " * self.tab_length)
            except (TypeError, AttributeError, ValueError):
                pass

        if self.is_escape_html_tag:
            try:
                data = html.escape(data)
            except AttributeError:
                return (data, None)

        data = self.__process_line_break(data)
        data = self.__escape_formula_injection(data)
        data = self.__dequote(data)

        try:
            return (data, strip_ansi_escape(data))
        except TypeError:
            return (data, None)

    @staticmethod
    def __preprocess_data(data, strip_str):
        if strip_str is None:
            return data

        try:
            return data.strip(strip_str)
        except AttributeError:
            return data
        except UnicodeDecodeError:
            return MultiByteStrDecoder(data).unicode_str.strip(strip_str)
        except TypeError:
            # reach here when data and strip_str type are different
            if isinstance(data, bytes):
                return MultiByteStrDecoder(data).unicode_str.strip(strip_str)
            elif isinstance(strip_str, bytes):
                return data.strip(MultiByteStrDecoder(strip_str).unicode_str)

    def __dequote(self, s: str) -> str:
        if not self.dequote or not s:
            return s

        try:
            if (s[0] == s[-1]) and s.startswith(("'", '"')):
                if s.count(s[0]) == 2:
                    return s[1:-1]
        except TypeError:
            pass

        return s

    def __process_line_break(self, data):
        lbh = self.line_break_handling

        if lbh == LineBreakHandling.NOP:
            return data

        try:
            if lbh == LineBreakHandling.REPLACE:
                return _RE_LINE_BREAK.sub(self.line_break_repl, data)

            if lbh == LineBreakHandling.ESCAPE:
                return data.replace("\n", "\\n").replace("\r", "\\r")
        except (TypeError, AttributeError):
            return data

        raise ValueError(f"unexpected line_break_handling: {lbh}")

    def __escape_formula_injection(self, data):
        if not self.is_escape_formula_injection:
            return data

        try:
            if _RE_FORMULA_PREFIX.search(data):
                return "'" + data
        except (TypeError, AttributeError):
            return data

        return data
