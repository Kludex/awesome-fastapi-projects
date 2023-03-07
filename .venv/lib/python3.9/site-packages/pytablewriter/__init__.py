"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from dataproperty import LineBreakHandling

from .__version__ import __author__, __copyright__, __email__, __license__, __version__
from ._factory import TableWriterFactory
from ._function import dump_tabledata, dumps_tabledata
from ._logger import set_log_level, set_logger
from ._table_format import FormatAttr, TableFormat
from .error import (
    EmptyTableDataError,
    EmptyTableNameError,
    EmptyValueError,
    NotSupportedError,
    WriterNotFoundError,
)
from .style import Align, Format
from .typehint import (
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
    String,
)
from .writer import (
    AbstractTableWriter,
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
