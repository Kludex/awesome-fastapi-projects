from typing import List

import typepy
from mbstrdecoder import MultiByteStrDecoder

from ....error import EmptyTableNameError
from ._numpy import NumpyTableWriter


class PandasDataFrameWriter(NumpyTableWriter):
    """
    A writer class for Pandas DataFrame format.

        :Example:
            :ref:`example-pandas-dataframe-writer`

    .. py:attribute:: import_pandas_as
        :type: str
        :value: "pd"

        Specify ``pandas`` module import name of an output source code.

    .. py:attribute:: import_numpy_as
        :type: str
        :value: "np"

        Specify ``numpy`` module import name of an output source code.

    .. py:method:: write_table

        |write_table| with Pandas DataFrame format.
        The tabular data are written as a ``pandas.DataFrame`` class
        instance definition.

        :raises pytablewriter.EmptyTableNameError:
            If the |table_name| is empty.

        :Example:
            :ref:`example-pandas-dataframe-writer`

        .. note::
            Specific values in the tabular data are converted when writing:

            - |None|: written as ``None``
            - |inf|: written as ``numpy.inf``
            - |nan|: written as ``numpy.nan``
            - |datetime| instances determined by |is_datetime_instance_formatting| attribute:
                - |True|: written as `dateutil.parser <https://dateutil.readthedocs.io/en/stable/parser.html>`__
                - |False|: written as |str|

            .. seealso::
                :ref:`example-type-hint-python`
    """

    FORMAT_NAME = "pandas"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.import_pandas_as = "pd"
        self.is_write_header = False

    def _get_opening_row_items(self) -> List[str]:
        return [f"{self.variable_name} = {self.import_pandas_as}.DataFrame(["]

    def _get_closing_row_items(self) -> List[str]:
        if typepy.is_not_empty_sequence(self.headers):
            return [
                "], columns=[{}])".format(
                    ", ".join(
                        f'"{MultiByteStrDecoder(header).unicode_str}"' for header in self.headers
                    )
                )
            ]

        return ["])"]

    def _verify_property(self) -> None:
        super()._verify_property()

        if typepy.is_null_string(self.table_name):
            raise EmptyTableNameError("table_name must be a string of one or more characters")
