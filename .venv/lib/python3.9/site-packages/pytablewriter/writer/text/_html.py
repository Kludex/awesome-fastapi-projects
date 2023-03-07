import copy
import warnings
from typing import Any, Optional, Tuple, cast

import dataproperty
import typepy
from mbstrdecoder import MultiByteStrDecoder
from pathvalidate import replace_symbol

from ...error import EmptyTableDataError
from ...sanitizer import sanitize_python_var_name
from ...style import Align, FontStyle, FontWeight, HtmlStyler, Style, StylerInterface, VerticalAlign
from .._common import import_error_msg_template
from .._table_writer import AbstractTableWriter
from ._css import CssTableWriter
from ._text_writer import TextTableWriter


def _get_tags_module() -> Tuple:
    try:
        from dominate import tags
        from dominate.util import raw

        return tags, raw
    except ImportError:
        warnings.warn(import_error_msg_template.format("html"))
        raise


class HtmlTableWriter(TextTableWriter):
    """
    A table writer class for HTML format.

        :Example:
            :ref:`example-html-table-writer`
    """

    FORMAT_NAME = "html"

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

        self._dp_extractor.preprocessor.line_break_repl = "<br>"
        self._dp_extractor.preprocessor.is_escape_html_tag = False
        self._quoting_flags = copy.deepcopy(dataproperty.NOT_QUOTING_FLAGS)
        self._table_tag: Any = None

        self.enable_ansi_escape = False

    def write_table(self, **kwargs) -> None:
        """
        |write_table| with HTML table format.

        Args:
            write_css (bool):
                If |True|, write CSS corresponding to the specified styles,
                instead of attributes of HTML tags.

        Example:
            :ref:`example-html-table-writer`

        .. note::
            - |None| values will be replaced with an empty value
        """

        tags, raw = _get_tags_module()
        write_css = kwargs.get("write_css", False)

        with self._logger:
            try:
                self._verify_property()
            except EmptyTableDataError:
                self._logger.logger.debug("no tabular data found")
                return

            self._preprocess()

            css_class = None

            if write_css:
                css_class = kwargs.get(
                    "css_class",
                    "{}-css".format(replace_symbol(self.table_name, replacement_text="-")),
                )

                css_writer = CssTableWriter(table_name=css_class)
                css_writer.from_writer(self, is_overwrite_table_name=False)
                css_writer.write_table(write_style_tag=True)

            if typepy.is_not_null_string(self.table_name):
                if css_class:
                    self._table_tag = tags.table(
                        id=sanitize_python_var_name(self.table_name), class_name=css_class
                    )
                else:
                    self._table_tag = tags.table(id=sanitize_python_var_name(self.table_name))
                self._table_tag += tags.caption(MultiByteStrDecoder(self.table_name).unicode_str)
            else:
                self._table_tag = tags.table()

            try:
                self._write_header()
            except ValueError:
                pass

            self._write_body(not write_css)

    def _write_header(self) -> None:
        tags, raw = _get_tags_module()

        if not self.is_write_header:
            return

        if typepy.is_empty_sequence(self._table_headers):
            raise ValueError("headers is empty")

        tr_tag = tags.tr()
        for header in self._table_headers:
            tr_tag += tags.th(raw(MultiByteStrDecoder(header).unicode_str))

        thead_tag = tags.thead()
        thead_tag += tr_tag

        self._table_tag += thead_tag

    def _write_body(self, write_attr: bool) -> None:
        tags, raw = _get_tags_module()
        tbody_tag = tags.tbody()

        for row_idx, (values, value_dp_list) in enumerate(
            zip(self._table_value_matrix, self._table_value_dp_matrix)
        ):
            tr_tag = tags.tr()
            for value, value_dp, column_dp in zip(values, value_dp_list, self._column_dp_list):
                td_tag = tags.td(raw(MultiByteStrDecoder(value).unicode_str))

                default_style = self._get_col_style(column_dp.column_index)
                style = self._fetch_style_from_filter(row_idx, column_dp, value_dp, default_style)

                if write_attr:
                    if style.align == Align.AUTO:
                        td_tag["align"] = value_dp.align.align_string
                    else:
                        td_tag["align"] = style.align.align_string

                    if style.vertical_align != VerticalAlign.BASELINE:
                        td_tag["valign"] = style.vertical_align.align_str

                    style_tag = self.__make_style_tag(style=style)
                    if style_tag:
                        td_tag["style"] = style_tag

                tr_tag += td_tag
            tbody_tag += tr_tag

        self._table_tag += tbody_tag
        self._write_line(self._table_tag.render(indent=self.indent_string))

    def __make_style_tag(self, style: Style) -> Optional[str]:
        styles = []  # List[str]

        if self._styler.get_font_size(style):
            styles.append(cast(str, self._styler.get_font_size(style)))
        if style.font_weight == FontWeight.BOLD:
            styles.append("font-weight:bold")
        if style.font_style == FontStyle.ITALIC:
            styles.append("font-style:italic")

        if not styles:
            return None

        return "; ".join(styles)

    def _create_styler(self, writer: AbstractTableWriter) -> StylerInterface:
        return HtmlStyler(writer)
