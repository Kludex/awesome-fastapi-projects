"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import copy
from typing import Dict, Generator

import dataproperty
from dataproperty import ColumnDataProperty
from typepy import Typecode

from ..error import EmptyValueError
from ._msgfy import to_error_message
from ._table_writer import AbstractTableWriter


def _get_es_datatype(column_dp: ColumnDataProperty) -> Dict[str, str]:
    if column_dp.typecode in (
        Typecode.NONE,
        Typecode.NULL_STRING,
        Typecode.INFINITY,
        Typecode.NAN,
    ):
        return {"type": "keyword"}

    if column_dp.typecode == Typecode.STRING:
        return {"type": "text"}

    if column_dp.typecode == Typecode.DATETIME:
        return {"type": "date", "format": "date_optional_time"}

    if column_dp.typecode == Typecode.REAL_NUMBER:
        return {"type": "double"}

    if column_dp.typecode == Typecode.BOOL:
        return {"type": "boolean"}

    if column_dp.typecode == Typecode.IP_ADDRESS:
        return {"type": "ip"}

    if column_dp.typecode == Typecode.INTEGER:
        assert column_dp.bit_length is not None

        if column_dp.bit_length <= 8:
            return {"type": "byte"}
        elif column_dp.bit_length <= 16:
            return {"type": "short"}
        elif column_dp.bit_length <= 32:
            return {"type": "integer"}
        elif column_dp.bit_length <= 64:
            return {"type": "long"}

        raise ValueError(
            f"too large integer bits: expected<=64bits, actual={column_dp.bit_length:d}bits"
        )

    raise ValueError(f"unknown typecode: {column_dp.typecode}")


class ElasticsearchWriter(AbstractTableWriter):
    """
    A table writer class for Elasticsearch.

    :Dependency Packages:
        - `elasticsearch-py <https://github.com/elastic/elasticsearch-py>`__

    .. py:attribute:: index_name
        :type: str

        Alias attribute for |table_name|.

    .. py:attribute:: document_type
        :type: str
        :value: "table"

        Specify document type for indices.

    .. py:method:: write_table()

        Create an index and put documents for each row to Elasticsearch.

        You need to pass an
        `elasticsearch.Elasticsearch <https://elasticsearch-py.rtfd.io/en/master/api.html#elasticsearch>`__
        instance to |stream| before calling this method.
        |table_name|/:py:attr:`~pytablewriter.ElasticsearchWriter.index_name`
        used as the creating index name,
        invalid characters in the name are replaced with underscore (``'_'``).
        Document data types for documents are automatically detected
        from the data.

        :raises ValueError:
            If the |stream| has not elasticsearch.Elasticsearch instance.
        :Example:
            :ref:`example-elasticsearch-table-writer`
    """

    FORMAT_NAME = "elasticsearch"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return True

    @property
    def table_name(self) -> str:
        return super().table_name

    @table_name.setter
    def table_name(self, value) -> None:
        from pathvalidate import ErrorReason, ValidationError

        from ..sanitizer import ElasticsearchIndexNameSanitizer

        try:
            self._table_name = ElasticsearchIndexNameSanitizer(value).sanitize(replacement_text="_")
        except ValidationError as e:
            if e.reason is ErrorReason.NULL_NAME:
                self._table_name = ""
            else:
                raise

    @property
    def index_name(self) -> str:
        return self.table_name

    @index_name.setter
    def index_name(self, value: str) -> None:
        self.table_name = value

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.stream = None
        self.is_padding = False
        self.is_formatting_float = False
        self._is_require_table_name = True
        self._quoting_flags = copy.deepcopy(dataproperty.NOT_QUOTING_FLAGS)
        self._dp_extractor.type_value_map = copy.deepcopy(dataproperty.DefaultValue.TYPE_VALUE_MAP)

        self.document_type = "table"

    def write_null_line(self) -> None:
        pass

    def _get_mappings(self) -> Dict[str, Dict]:
        properties = {}

        for header, column_dp in zip(self.headers, self._column_dp_list):
            properties[header] = _get_es_datatype(column_dp)

        return {"mappings": {self.document_type: {"properties": properties}}}

    def _get_body(self) -> Generator:
        str_datatype = (Typecode.DATETIME, Typecode.IP_ADDRESS, Typecode.INFINITY, Typecode.NAN)

        for value_dp_list in self._table_value_dp_matrix:
            values = [
                value_dp.data if value_dp.typecode not in str_datatype else value_dp.to_str()
                for value_dp in value_dp_list
            ]

            yield dict(zip(self.headers, values))

    def _write_table(self, **kwargs) -> None:
        import elasticsearch as es

        if not isinstance(self.stream, es.Elasticsearch):
            raise ValueError("stream must be an elasticsearch.Elasticsearch instance")

        try:
            self._verify_value_matrix()
        except EmptyValueError:
            self._logger.logger.debug("no tabular data found")
            return

        self._preprocess()

        mappings = self._get_mappings()

        try:
            result = self.stream.indices.create(index=self.index_name, body=mappings)
            self._logger.logger.debug(result)
        except es.TransportError as e:
            if e.error == "index_already_exists_exception":
                # ignore already existing index
                self._logger.logger.debug(to_error_message(e))
            else:
                raise

        for body in self._get_body():
            try:
                self.stream.index(index=self.index_name, body=body, doc_type=self.document_type)
            except es.exceptions.RequestError as e:
                self._logger.logger.error(f"{to_error_message(e)}, body={body}")

    def _write_value_row_separator(self) -> None:
        pass
