import copy
import warnings
from typing import Any, Dict, List, Union

import dataproperty

from .._common import import_error_msg_template
from ._common import serialize_dp
from ._text_writer import TextTableWriter


class YamlTableWriter(TextTableWriter):
    """
    A table writer class for `YAML <https://yaml.org/>`__ format.

        :Example:
            :ref:`example-yaml-table-writer`
    """

    FORMAT_NAME = "yaml"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.is_padding = False

        self._dp_extractor.float_type = float
        self._quoting_flags = copy.deepcopy(dataproperty.NOT_QUOTING_FLAGS)

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self) -> bool:
        return False

    def write_table(self, **kwargs) -> None:
        """
        |write_table| with
        YAML format.

        :Example:
            :ref:`example-yaml-table-writer`
        """

        try:
            import yaml
        except ImportError:
            warnings.warn(import_error_msg_template.format("yaml"))
            raise

        with self._logger:
            self._verify_property()
            self._preprocess()

            if self.headers:
                matrix: List[Union[Dict[str, Any], List[Any]]] = [
                    dict(zip(self.headers, [serialize_dp(value_dp) for value_dp in value_dp_list]))
                    for value_dp_list in self._table_value_dp_matrix
                ]
            else:
                matrix = [
                    [serialize_dp(value_dp) for value_dp in value_dp_list]
                    for value_dp_list in self._table_value_dp_matrix
                ]

            if self.table_name:
                self._write(yaml.safe_dump({self.table_name: matrix}, default_flow_style=False))
            else:
                self._write(yaml.safe_dump(matrix, default_flow_style=False))
