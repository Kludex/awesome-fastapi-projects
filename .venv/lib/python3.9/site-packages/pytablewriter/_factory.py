"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import os
from itertools import chain
from typing import List

import typepy

from ._logger import logger
from ._table_format import FormatAttr, TableFormat
from .error import WriterNotFoundError
from .writer._table_writer import AbstractTableWriter


class TableWriterFactory:
    """
    A factor class of table writer classes.
    """

    @classmethod
    def create_from_file_extension(cls, file_extension: str, **kwargs) -> AbstractTableWriter:
        """
        Create a table writer class instance from a file extension.
        Supported file extensions are as follows:

            ==================  ===================================
            Extension           Writer Class
            ==================  ===================================
            ``".adoc"``         :py:class:`~.AsciiDocTableWriter`
            ``".asciidoc"``     :py:class:`~.AsciiDocTableWriter`
            ``".asc"``          :py:class:`~.AsciiDocTableWriter`
            ``".css"``          :py:class:`~.CssTableWriter`
            ``".csv"``          :py:class:`~.CsvTableWriter`
            ``".htm"``          :py:class:`~.HtmlTableWriter`
            ``".html"``         :py:class:`~.HtmlTableWriter`
            ``".js"``           :py:class:`~.JavaScriptTableWriter`
            ``".json"``         :py:class:`~.JsonTableWriter`
            ``".jsonl"``        :py:class:`~.JsonLinesTableWriter`
            ``".ltsv"``         :py:class:`~.LtsvTableWriter`
            ``".ldjson"``       :py:class:`~.JsonLinesTableWriter`
            ``".md"``           :py:class:`~.MarkdownTableWriter`
            ``".ndjson"``       :py:class:`~.JsonLinesTableWriter`
            ``".py"``           :py:class:`~.PythonCodeTableWriter`
            ``".rst"``          :py:class:`~.RstGridTableWriter`
            ``".tsv"``          :py:class:`~.TsvTableWriter`
            ``".xls"``          :py:class:`~.ExcelXlsTableWriter`
            ``".xlsx"``         :py:class:`~.ExcelXlsxTableWriter`
            ``".sqlite"``       :py:class:`~.SqliteTableWriter`
            ``".sqlite3"``      :py:class:`~.SqliteTableWriter`
            ``".tsv"``          :py:class:`~.TsvTableWriter`
            ``".toml"``         :py:class:`~.TomlTableWriter`
            ``".yml"``          :py:class:`~.YamlTableWriter`
            ==================  ===================================

        :param str file_extension:
            File extension string (case insensitive).
        :param kwargs:
            Keyword arguments that passing to writer class constructor.
        :return:
            Writer instance that coincides with the ``file_extension``.
        :rtype:
            :py:class:`~pytablewriter.writer._table_writer.TableWriterInterface`
        :raises pytablewriter.WriterNotFoundError:
            |WriterNotFoundError_desc| the file extension.
        """

        ext = os.path.splitext(file_extension)[1]
        if typepy.is_null_string(ext):
            file_extension = file_extension
        else:
            file_extension = ext

        file_extension = file_extension.lstrip(".").lower()

        for table_format in TableFormat:
            if file_extension not in table_format.file_extensions:
                continue

            if table_format.format_attribute & FormatAttr.SECONDARY_EXT:
                continue

            logger.debug(f"create a {table_format.writer_class.__name__} instance")

            return table_format.writer_class(**kwargs)

        raise WriterNotFoundError(
            "\n".join(
                [
                    f"{file_extension:s} (unknown file extension).",
                    "",
                    "acceptable file extensions are: {}.".format(", ".join(cls.get_extensions())),
                ]
            )
        )

    @classmethod
    def create_from_format_name(cls, format_name: str, **kwargs) -> AbstractTableWriter:
        """
        Create a table writer class instance from a format name.
        Supported file format names are as follows:

            =============================================  ===================================
            Format name                                    Writer Class
            =============================================  ===================================
            ``"adoc"``                                     :py:class:`~.AsciiDocTableWriter`
            ``"asciidoc"``                                 :py:class:`~.AsciiDocTableWriter`
            ``"css"``                                      :py:class:`~.CssTableWriter`
            ``"csv"``                                      :py:class:`~.CsvTableWriter`
            ``"elasticsearch"``                            :py:class:`~.ElasticsearchWriter`
            ``"excel"``                                    :py:class:`~.ExcelXlsxTableWriter`
            ``"html"``/``"htm"``                           :py:class:`~.HtmlTableWriter`
            ``"javascript"``/``"js"``                      :py:class:`~.JavaScriptTableWriter`
            ``"json"``                                     :py:class:`~.JsonTableWriter`
            ``"json_lines"``                               :py:class:`~.JsonLinesTableWriter`
            ``"latex_matrix"``                             :py:class:`~.LatexMatrixWriter`
            ``"latex_table"``                              :py:class:`~.LatexTableWriter`
            ``"ldjson"``                                   :py:class:`~.JsonLinesTableWriter`
            ``"ltsv"``                                     :py:class:`~.LtsvTableWriter`
            ``"markdown"``/``"md"``                        :py:class:`~.MarkdownTableWriter`
            ``"mediawiki"``                                :py:class:`~.MediaWikiTableWriter`
            ``"null"``                                     :py:class:`~.NullTableWriter`
            ``"pandas"``                                   :py:class:`~.PandasDataFrameWriter`
            ``"py"``/``"python"``                          :py:class:`~.PythonCodeTableWriter`
            ``"rst"``/``"rst_grid"``/``"rst_grid_table"``  :py:class:`~.RstGridTableWriter`
            ``"rst_simple"``/``"rst_simple_table"``        :py:class:`~.RstSimpleTableWriter`
            ``"rst_csv"``/``"rst_csv_table"``              :py:class:`~.RstCsvTableWriter`
            ``"sqlite"``                                   :py:class:`~.SqliteTableWriter`
            ``"ssv"``                                      :py:class:`~.SpaceAlignedTableWriter`
            ``"tsv"``                                      :py:class:`~.TsvTableWriter`
            ``"toml"``                                     :py:class:`~.TomlTableWriter`
            ``"unicode"``                                  :py:class:`~.UnicodeTableWriter`
            ``"yaml"``                                     :py:class:`~.YamlTableWriter`
            =============================================  ===================================

        :param str format_name: Format name string (case insensitive).
        :param kwargs:
            Keyword arguments that passing to writer class constructor.
        :return: Writer instance that coincides with the ``format_name``:
        :rtype:
            :py:class:`~pytablewriter.writer._table_writer.TableWriterInterface`
        :raises pytablewriter.WriterNotFoundError:
            |WriterNotFoundError_desc| for the format.
        """

        format_name = format_name.casefold()

        for table_format in TableFormat:
            if format_name in table_format.names and not (
                table_format.format_attribute & FormatAttr.SECONDARY_NAME
            ):
                logger.debug(f"create a {table_format.writer_class.__name__} instance")

                return table_format.writer_class(**kwargs)

        raise WriterNotFoundError(
            "\n".join(
                [
                    f"{format_name} (unknown format name).",
                    "acceptable format names are: {}.".format(", ".join(cls.get_format_names())),
                ]
            )
        )

    @classmethod
    def get_format_names(cls) -> List[str]:
        """
        :return: Available format names.
        :rtype: list

        :Example:
            .. code:: python

                >>> import pytablewriter as ptw
                >>> for name in ptw.TableWriterFactory.get_format_names():
                ...     print(name)
                ...
                adoc
                asciidoc
                bold_unicode
                borderless
                css
                csv
                elasticsearch
                excel
                htm
                html
                javascript
                js
                json
                json_lines
                jsonl
                latex_matrix
                latex_table
                ldjson
                ltsv
                markdown
                md
                mediawiki
                ndjson
                null
                numpy
                pandas
                pandas_pickle
                py
                python
                rst
                rst_csv
                rst_csv_table
                rst_grid
                rst_grid_table
                rst_simple
                rst_simple_table
                space_aligned
                sqlite
                ssv
                toml
                tsv
                unicode
                yaml

        """

        return sorted(list(set(chain(*(table_format.names for table_format in TableFormat)))))

    @classmethod
    def get_extensions(cls) -> List[str]:
        """
        :return: Available file extensions.
        :rtype: list

        :Example:
            .. code:: python

                >>> import pytablewriter as ptw
                >>> for name in ptw.TableWriterFactory.get_extensions():
                ...     print(name)
                ...
                adoc
                asc
                asciidoc
                css
                csv
                htm
                html
                js
                json
                jsonl
                ldjson
                ltsv
                md
                ndjson
                py
                rst
                sqlite
                sqlite3
                tex
                toml
                tsv
                xls
                xlsx
                yml
        """

        file_extension_set = set()
        for table_format in TableFormat:
            for file_extension in table_format.file_extensions:
                file_extension_set.add(file_extension)

        return sorted(list(file_extension_set))
