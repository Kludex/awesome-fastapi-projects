"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import enum
from typing import Any, List

from .writer import (
    AsciiDocTableWriter,
    BoldUnicodeTableWriter,
    BorderlessTableWriter,
    CssTableWriter,
    CsvTableWriter,
    ElasticsearchWriter,
    ExcelXlsTableWriter,
    ExcelXlsxTableWriter,
    HtmlTableWriter,
    JavaScriptTableWriter,
    JsonLinesTableWriter,
    JsonTableWriter,
    LatexMatrixWriter,
    LatexTableWriter,
    LtsvTableWriter,
    MarkdownTableWriter,
    MediaWikiTableWriter,
    NullTableWriter,
    NumpyTableWriter,
    PandasDataFramePickleWriter,
    PandasDataFrameWriter,
    PythonCodeTableWriter,
    RstCsvTableWriter,
    RstGridTableWriter,
    RstSimpleTableWriter,
    SpaceAlignedTableWriter,
    SqliteTableWriter,
    TomlTableWriter,
    TsvTableWriter,
    UnicodeTableWriter,
    YamlTableWriter,
)


class FormatAttr:
    """
    Bitmaps to represent table attributes.
    """

    NONE = 1 << 1

    #: Can create a file with the format.
    FILE = 1 << 2

    #: Table format that can represent as a text.
    TEXT = 1 << 3

    #: Table format that can represent as a binary file.
    BIN = 1 << 4

    #: Can create a source code (variables definition)
    #: one of the programming language.
    SOURCECODE = 1 << 5

    #: Can call API for external service.
    API = 1 << 6

    SECONDARY_EXT = 1 << 10
    SECONDARY_NAME = 1 << 11


@enum.unique
class TableFormat(enum.Enum):
    """
    Enum to represent table format attributes.
    """

    ASCIIDOC = (
        [AsciiDocTableWriter.FORMAT_NAME, "adoc"],
        AsciiDocTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        ["adoc", "asciidoc", "asc"],
    )
    CSV = ([CsvTableWriter.FORMAT_NAME], CsvTableWriter, FormatAttr.FILE | FormatAttr.TEXT, ["csv"])
    CSS = (
        [CssTableWriter.FORMAT_NAME],
        CssTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        ["css"],
    )
    ELASTICSEARCH = (
        [ElasticsearchWriter.FORMAT_NAME],  # type: ignore
        ElasticsearchWriter,
        FormatAttr.API,
        [],
    )
    EXCEL_XLSX = (
        [ExcelXlsxTableWriter.FORMAT_NAME],
        ExcelXlsxTableWriter,
        FormatAttr.FILE | FormatAttr.BIN,
        ["xlsx"],
    )
    EXCEL_XLS = (
        [ExcelXlsTableWriter.FORMAT_NAME],
        ExcelXlsTableWriter,
        FormatAttr.FILE | FormatAttr.BIN | FormatAttr.SECONDARY_NAME,
        ["xls"],
    )
    HTML = (
        [HtmlTableWriter.FORMAT_NAME, "htm"],
        HtmlTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        ["html", "htm"],
    )
    JAVASCRIPT = (
        [JavaScriptTableWriter.FORMAT_NAME, "js"],
        JavaScriptTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT | FormatAttr.SOURCECODE,
        ["js"],
    )
    JSON = (
        [JsonTableWriter.FORMAT_NAME],
        JsonTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        ["json"],
    )
    JSON_LINES = (
        [JsonLinesTableWriter.FORMAT_NAME, "jsonl", "ldjson", "ndjson"],
        JsonLinesTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        ["jsonl", "ldjson", "ndjson"],
    )
    LATEX_MATRIX = (
        [LatexMatrixWriter.FORMAT_NAME],
        LatexMatrixWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        ["tex"],
    )
    LATEX_TABLE = (
        [LatexTableWriter.FORMAT_NAME],
        LatexTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT | FormatAttr.SECONDARY_EXT,
        ["tex"],
    )
    LTSV = (
        [LtsvTableWriter.FORMAT_NAME],
        LtsvTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        ["ltsv"],
    )
    MARKDOWN = (
        [MarkdownTableWriter.FORMAT_NAME, "md"],
        MarkdownTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        ["md"],
    )
    MEDIAWIKI = (
        [MediaWikiTableWriter.FORMAT_NAME],  # type: ignore
        MediaWikiTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        [],
    )
    NULL = (
        [NullTableWriter.FORMAT_NAME],  # type: ignore
        NullTableWriter,
        FormatAttr.NONE,
        [],
    )
    NUMPY = (
        [NumpyTableWriter.FORMAT_NAME],
        NumpyTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT | FormatAttr.SOURCECODE | FormatAttr.SECONDARY_EXT,
        ["py"],
    )
    PANDAS = (
        [PandasDataFrameWriter.FORMAT_NAME],
        PandasDataFrameWriter,
        FormatAttr.FILE | FormatAttr.TEXT | FormatAttr.SOURCECODE | FormatAttr.SECONDARY_EXT,
        ["py"],
    )
    PANDAS_PICKLE = (
        [PandasDataFramePickleWriter.FORMAT_NAME],  # type: ignore
        PandasDataFramePickleWriter,
        FormatAttr.FILE | FormatAttr.BIN,
        [],
    )
    PYTHON = (
        [PythonCodeTableWriter.FORMAT_NAME, "py"],
        PythonCodeTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT | FormatAttr.SOURCECODE,
        ["py"],
    )
    RST_CSV_TABLE = (
        [RstCsvTableWriter.FORMAT_NAME, "rst_csv"],
        RstCsvTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT | FormatAttr.SECONDARY_EXT,
        ["rst"],
    )
    RST_GRID_TABLE = (
        [RstGridTableWriter.FORMAT_NAME, "rst_grid", "rst"],
        RstGridTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        ["rst"],
    )
    RST_SIMPLE_TABLE = (
        [RstSimpleTableWriter.FORMAT_NAME, "rst_simple"],
        RstSimpleTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT | FormatAttr.SECONDARY_EXT,
        ["rst"],
    )
    SPACE_ALIGNED = (
        [SpaceAlignedTableWriter.FORMAT_NAME, "ssv"],  # type: ignore
        SpaceAlignedTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        [],
    )
    SQLITE = (
        [SqliteTableWriter.FORMAT_NAME],
        SqliteTableWriter,
        FormatAttr.FILE | FormatAttr.BIN,
        ["sqlite", "sqlite3"],
    )
    TOML = (
        [TomlTableWriter.FORMAT_NAME],
        TomlTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        ["toml"],
    )
    TSV = ([TsvTableWriter.FORMAT_NAME], TsvTableWriter, FormatAttr.FILE | FormatAttr.TEXT, ["tsv"])
    UNICODE = (
        [UnicodeTableWriter.FORMAT_NAME],  # type: ignore
        UnicodeTableWriter,
        FormatAttr.TEXT,
        [],
    )
    YAML = (
        [YamlTableWriter.FORMAT_NAME],
        YamlTableWriter,
        FormatAttr.FILE | FormatAttr.TEXT,
        ["yml"],
    )
    BOLD_UNICODE = (
        [BoldUnicodeTableWriter.FORMAT_NAME],  # type: ignore
        BoldUnicodeTableWriter,
        FormatAttr.TEXT,
        [],
    )
    BORDERLESS = (
        [BorderlessTableWriter.FORMAT_NAME],  # type: ignore
        BorderlessTableWriter,
        FormatAttr.TEXT,
        [],
    )

    @property
    def names(self) -> List[str]:
        """Names associated with the table format.

        Returns:
            List[str]: format names
        """

        return self.__names

    @property
    def writer_class(self) -> Any:
        """Table writer class object associated with the table format.

        Returns:
            Type[AbstractTableWriter]:
        """

        return self.__writer_class

    @property
    def format_attribute(self) -> int:
        """Table attributes bitmap.

        Returns:
            :py:class:`pytablewriter.FormatAttr`:
        """

        return self.__format_attribute

    @property
    def file_extensions(self) -> List[str]:
        """File extensions associated with the table format.

        Returns:
            List[str]:
        """

        return self.__file_extensions

    def __init__(self, names, writer_class, format_attribute, file_extensions):
        self.__names = names
        self.__writer_class = writer_class
        self.__format_attribute = format_attribute
        self.__file_extensions = file_extensions

    @classmethod
    def find_all_attr(cls, format_attribute: int) -> List:
        """Searching table formats which have specific attributes.

        Args:
            format_attribute (FormatAttr):
                Table format attributes to look for.

        Returns:
            List[TableFormat]: Table formats that matched the attribute.
        """

        return [
            table_format
            for table_format in TableFormat
            if table_format.format_attribute & format_attribute
        ]

    @classmethod
    def from_name(cls, format_name: str):
        """Get a table format from a format name.

        Args:
            format_name (str): Table format specifier.

        Returns:
            Optional[TableFormat]: A table format enum value corresponding to the ``format_name``.
        """

        format_name = format_name.casefold().strip()

        for table_format in TableFormat:
            if format_name in table_format.names:
                return table_format

        return None

    @classmethod
    def from_file_extension(cls, file_extension: str):
        """Get a table format from a file extension.

        Args:
            file_extension (str): File extension.

        Returns:
            Optional[TableFormat]:
                A table format enum value corresponding to the ``file_extension``.
        """

        ext = file_extension.lower().strip().lstrip(".")

        for table_format in TableFormat:
            if ext in table_format.file_extensions:
                return table_format

        return None
