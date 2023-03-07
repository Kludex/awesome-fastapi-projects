import copy
from typing import List, cast

from dataproperty import NOT_QUOTING_FLAGS, DataProperty
from pathvalidate import replace_symbol

from ...error import EmptyTableDataError
from ...style import Align, DecorationLine, FontStyle, FontWeight, Style, VerticalAlign
from ._text_writer import IndentationTextTableWriter


class CssTableWriter(IndentationTextTableWriter):
    """
    A CSS writer class.
    """

    FORMAT_NAME = "css"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return False

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.is_padding = False
        self.indent_string = kwargs.get("indent_string", "    ")

        self._dp_extractor.preprocessor.is_escape_html_tag = False
        self._quoting_flags = copy.deepcopy(NOT_QUOTING_FLAGS)

    def write_table(self, **kwargs) -> None:
        """
        |write_table| with CSS.
        """

        with self._logger:
            try:
                self._verify_property()
            except EmptyTableDataError:
                self._logger.logger.debug("no tabular data found")
                return

            self._preprocess()

            self.__write_css(
                css_class=replace_symbol(self.table_name, replacement_text="-"),
                write_style_tag=kwargs.get("write_style_tag", False),
            )

    def __extract_css_tags(self, value_dp: DataProperty, style: Style) -> List[str]:
        css_tags = []  # List[str]

        if self._styler.get_font_size(style):
            css_tags.append(cast(str, self._styler.get_font_size(style)))
        if style.font_weight == FontWeight.BOLD:
            css_tags.append("font-weight:bold")
        if style.font_style == FontStyle.ITALIC:
            css_tags.append("font-style:italic")

        if style.color:
            css_tags.append(f"color: {style.color.color_code}")

        if style.bg_color:
            css_tags.append(f"background-color: {style.bg_color.color_code}")

        css_tag = self.__extract_align_tag(value_dp, style)
        if css_tag:
            css_tags.append(css_tag)

        if style.vertical_align != VerticalAlign.BASELINE:
            css_tags.append(f"vertical-align: {style.vertical_align.align_str}")

        if style.decoration_line in (DecorationLine.LINE_THROUGH, DecorationLine.STRIKE):
            css_tags.append("text-decoration-line: line-through")
        elif style.decoration_line == DecorationLine.UNDERLINE:
            css_tags.append("text-decoration-line: underline")

        return css_tags

    def __extract_align_tag(self, value_dp: DataProperty, style: Style) -> str:
        if style.align == Align.AUTO:
            value = value_dp.align.align_string
        else:
            value = style.align.align_string

        return f"text-align: {value}"

    def __write_css_thead(self, css_class: str, base_indent_level: int) -> None:
        for col_dp, header_dp in zip(self._column_dp_list, self._dp_extractor.to_header_dp_list()):
            default_style = self._get_col_style(col_dp.column_index)
            style = self._fetch_style_from_filter(-1, col_dp, header_dp, default_style)
            css_tags = self.__extract_css_tags(header_dp, style)

            if not css_tags:
                continue

            self.set_indent_level(base_indent_level)
            self._write_line(
                ".{css_class} thead th:nth-child({col}) {{".format(
                    css_class=css_class, col=col_dp.column_index + 1
                )
            )

            self.set_indent_level(base_indent_level + 1)
            for css_tag in css_tags:
                self._write_line(f"{css_tag};")

            self.set_indent_level(base_indent_level)
            self._write_line("}")

    def __write_css_tbody(self, css_class: str, base_indent_level: int) -> None:
        for row_idx, (values, value_dp_list) in enumerate(
            zip(self._table_value_matrix, self._table_value_dp_matrix)
        ):
            for value, value_dp, col_dp in zip(values, value_dp_list, self._column_dp_list):
                default_style = self._get_col_style(col_dp.column_index)
                style = self._fetch_style_from_filter(row_idx, col_dp, value_dp, default_style)
                css_tags = self.__extract_css_tags(value_dp, style)

                if not css_tags:
                    continue

                self.set_indent_level(base_indent_level)
                self._write_line(
                    ".{css_class} tbody tr:nth-child({row}) td:nth-child({col}) {{".format(
                        css_class=css_class, row=row_idx + 1, col=col_dp.column_index + 1
                    )
                )

                self.set_indent_level(base_indent_level + 1)
                for css_tag in css_tags:
                    self._write_line(f"{css_tag};")

                self.set_indent_level(base_indent_level)
                self._write_line("}")

    def __write_css(self, css_class: str, write_style_tag: bool = False) -> None:
        base_indent_level = 0

        if write_style_tag:
            self._write_line('<style type="text/css">')
            base_indent_level = 1

        self.__write_css_thead(css_class, base_indent_level)
        self.__write_css_tbody(css_class, base_indent_level)

        if write_style_tag:
            self.set_indent_level(0)
            self._write_line("</style>")
