import warnings
from decimal import Decimal

import typepy

from .._common import import_error_msg_template
from ._common import serialize_dp
from ._text_writer import TextTableWriter


class TomlTableWriter(TextTableWriter):
    """
    A table writer class for
    `TOML <https://github.com/toml-lang/toml>`__ data format.

        :Example:
            :ref:`example-toml-table-writer`
    """

    FORMAT_NAME = "toml"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def support_split_write(self):
        return True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.is_formatting_float = False

        self._is_require_table_name = True
        self._is_require_header = True

    def write_table(self, **kwargs) -> None:
        """
        |write_table| with
        `TOML <https://github.com/toml-lang/toml>`__ format.

        :raises pytablewriter.EmptyTableNameError:
            If the |headers| is empty.
        :Example:
            :ref:`example-toml-table-writer`
        """

        try:
            import toml

            class TomlTableEncoder(toml.encoder.TomlEncoder):
                def __init__(self, _dict=dict, preserve=False):
                    super().__init__(_dict=_dict, preserve=preserve)

                    self.dump_funcs[str] = str
                    self.dump_funcs[Decimal] = toml.encoder._dump_float

        except ImportError:
            warnings.warn(import_error_msg_template.format("toml"))
            raise

        with self._logger:
            self._verify_property()
            self._preprocess()

            body = []
            for value_dp_list in self._table_value_dp_matrix:
                row = {}

                for header, value in zip(
                    self.headers,
                    [serialize_dp(value_dp) for value_dp in value_dp_list],
                ):
                    if typepy.is_null_string(value):
                        continue

                    row[header] = value

                body.append(row)

            self.stream.write(toml.dumps({self.table_name: body}, encoder=TomlTableEncoder()))
