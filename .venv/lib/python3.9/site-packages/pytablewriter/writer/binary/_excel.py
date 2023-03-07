import abc
import copy
import warnings
from typing import Any, Dict, Optional, cast

import dataproperty
import typepy
from dataproperty import DataProperty
from tabledata import TableData
from typepy import Integer

from .._common import import_error_msg_template
from ._excel_workbook import ExcelWorkbookInterface, ExcelWorkbookXls, ExcelWorkbookXlsx
from ._interface import AbstractBinaryTableWriter


class ExcelTableWriter(AbstractBinaryTableWriter, metaclass=abc.ABCMeta):
    """
    An abstract class of a table writer for Excel file format.
    """

    FORMAT_NAME = "excel"

    @property
    def format_name(self) -> str:
        return self.FORMAT_NAME

    @property
    def workbook(self) -> Optional[ExcelWorkbookInterface]:
        return self._workbook

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._workbook: Optional[ExcelWorkbookInterface] = None

        self._dp_extractor.type_value_map = {
            typepy.Typecode.INFINITY: "Inf",
            typepy.Typecode.NAN: "NaN",
        }

        self._first_header_row = 0
        self._last_header_row = self.first_header_row
        self._first_data_row = self.last_header_row + 1
        self._first_data_col = 0
        self._last_data_row: Optional[int] = None
        self._last_data_col: Optional[int] = None

        self._current_data_row = self._first_data_row

        self._quoting_flags = copy.deepcopy(dataproperty.NOT_QUOTING_FLAGS)
        self._quoting_flags[typepy.Typecode.DATETIME] = True

    @property
    def first_header_row(self) -> int:
        """
        :return: Index of the first row of the header.
        :rtype: int

        .. note:: |excel_attr|
        """

        return self._first_header_row

    @property
    def last_header_row(self) -> int:
        """
        :return: Index of the last row of the header.
        :rtype: int

        .. note:: |excel_attr|
        """

        return self._last_header_row

    @property
    def first_data_row(self) -> int:
        """
        :return: Index of the first row of the data (table body).
        :rtype: int

        .. note:: |excel_attr|
        """

        return self._first_data_row

    @property
    def last_data_row(self) -> Optional[int]:
        """
        :return: Index of the last row of the data (table body).
        :rtype: int

        .. note:: |excel_attr|
        """

        return self._last_data_row

    @property
    def first_data_col(self) -> int:
        """
        :return: Index of the first column of the table.
        :rtype: int

        .. note:: |excel_attr|
        """

        return self._first_data_col

    @property
    def last_data_col(self) -> Optional[int]:
        """
        :return: Index of the last column of the table.
        :rtype: int

        .. note:: |excel_attr|
        """

        return self._last_data_col

    def is_opened(self) -> bool:
        return self.workbook is not None

    def open(self, file_path: str) -> None:
        """
        Open an Excel workbook file.

        :param str file_path: Excel workbook file path to open.
        """

        if self.workbook and self.workbook.file_path == file_path:
            self._logger.logger.debug(f"workbook already opened: {self.workbook.file_path}")
            return

        self.close()
        self._open(file_path)

    @abc.abstractmethod
    def _open(self, workbook_path: str) -> None:  # pragma: no cover
        pass

    def close(self) -> None:
        """
        Close the current workbook.
        """

        if self.is_opened():
            self.workbook.close()  # type: ignore
            self._workbook = None

    def from_tabledata(self, value: TableData, is_overwrite_table_name: bool = True) -> None:
        """
        Set following attributes from |TableData|

        - :py:attr:`~.table_name`.
        - :py:attr:`~.headers`.
        - :py:attr:`~.value_matrix`.

        And create worksheet named from :py:attr:`~.table_name` ABC
        if not existed yet.

        :param tabledata.TableData value: Input table data.
        """

        super().from_tabledata(value)

        if self.is_opened():
            self.make_worksheet(self.table_name)

    def make_worksheet(self, sheet_name: Optional[str] = None) -> None:
        """Make a worksheet to the current workbook.

        Args:
            sheet_name (str):
                Name of the worksheet to create. The name will be automatically generated
                (like ``"Sheet1"``) if the ``sheet_name`` is empty.
        """

        if sheet_name is None:
            sheet_name = self.table_name
        if not sheet_name:
            sheet_name = ""

        self._stream = self.workbook.add_worksheet(sheet_name)  # type: ignore
        self._current_data_row = self._first_data_row

    def dump(self, output: str, close_after_write: bool = True, **kwargs) -> None:
        """Write a worksheet to the current workbook.

        Args:
            output (str):
                Path to the workbook file to write.
            close_after_write (bool, optional):
                Close the workbook after write.
                Defaults to |True|.
        """

        self.open(output)
        try:
            self.make_worksheet(self.table_name)
            self.write_table(**kwargs)
        finally:
            if close_after_write:
                self.close()

    @abc.abstractmethod
    def _write_header(self) -> None:
        pass

    @abc.abstractmethod
    def _write_cell(self, row: int, col: int, value_dp: DataProperty) -> None:
        pass

    def _write_table(self, **kwargs) -> None:
        self._preprocess_table_dp()
        self._preprocess_table_property()
        self._write_header()
        self._write_value_matrix()
        self._postprocess()

    def _write_value_matrix(self) -> None:
        for value_dp_list in self._table_value_dp_matrix:
            for col_idx, value_dp in enumerate(value_dp_list):
                self._write_cell(self._current_data_row, col_idx, value_dp)

            self._current_data_row += 1

    def _get_last_column(self) -> int:
        if typepy.is_not_empty_sequence(self.headers):
            return len(self.headers) - 1

        if typepy.is_not_empty_sequence(self.value_matrix):
            return len(self.value_matrix[0]) - 1

        raise ValueError("data not found")

    def _postprocess(self) -> None:
        self._last_data_row = self._current_data_row
        self._last_data_col = self._get_last_column()


class ExcelXlsTableWriter(ExcelTableWriter):
    """
    A table writer class for Excel file format: ``.xls`` (older or equal to Office 2003).

    ``xlwt`` package required to use this class.

    .. py:method:: write_table()

        Write a table to the current opened worksheet.

        :raises IOError: If failed to write data to the worksheet.

        .. note::
            Specific values in the tabular data are converted when writing:

            - |None|: written as an empty string
            - |inf|: written as ``Inf``
            - |nan|: written as ``NaN``
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.__col_style_table: Dict[int, Any] = {}

    def _open(self, workbook_path: str) -> None:
        self._workbook = ExcelWorkbookXls(workbook_path)

    def _write_header(self) -> None:
        if not self.is_write_header or typepy.is_empty_sequence(self.headers):
            return

        for col, value in enumerate(self.headers):
            self.stream.write(self.first_header_row, col, value)

    def _write_cell(self, row: int, col: int, value_dp: DataProperty) -> None:
        if value_dp.typecode in [typepy.Typecode.REAL_NUMBER]:
            try:
                cell_style = self.__get_cell_style(col)
            except ValueError:
                pass
            else:
                self.stream.write(row, col, value_dp.data, cell_style)
                return

        self.stream.write(row, col, value_dp.data)

    def _postprocess(self) -> None:
        super()._postprocess()

        self.__col_style_table = {}

    def __get_cell_style(self, col: int):
        try:
            import xlwt
        except ImportError:
            warnings.warn(import_error_msg_template.format("excel"))
            raise

        if col in self.__col_style_table:
            return self.__col_style_table.get(col)

        try:
            col_dp = self._column_dp_list[col]
        except KeyError:
            return {}

        if col_dp.typecode not in [typepy.Typecode.REAL_NUMBER]:
            raise ValueError()

        if not Integer(col_dp.minmax_decimal_places.max_value).is_type():
            raise ValueError()

        float_digit = col_dp.minmax_decimal_places.max_value
        if float_digit <= 0:
            raise ValueError()

        num_format_str = "#,{:s}0.{:s}".format("#" * int(float_digit), "0" * int(float_digit))
        cell_style = xlwt.easyxf(num_format_str=num_format_str)
        self.__col_style_table[col] = cell_style

        return cell_style


class ExcelXlsxTableWriter(ExcelTableWriter):
    """
    A table writer class for Excel file format: ``.xlsx`` (newer or equal to Office 2007).

    .. py:method:: write_table()

        Write a table to the current opened worksheet.

        :raises IOError: If failed to write data to the worksheet.
        :Examples:
            :ref:`example-excel-table-writer`

        .. note::
            Specific values in the tabular data are converted when writing:

            - |None|: written as an empty string
            - |inf|: written as ``Inf``
            - |nan|: written as ``NaN``
    """

    MAX_CELL_WIDTH = 60

    class TableFormat:
        HEADER = "header"
        CELL = "cell"
        NAN = "nan"

    class Default:
        FONT_NAME = "MS Gothic"
        FONT_SIZE = 9

        CELL_FORMAT = {
            "font_name": FONT_NAME,
            "font_size": FONT_SIZE,
            "align": "top",
            "text_wrap": True,
            "top": 1,
            "left": 1,
            "bottom": 1,
            "right": 1,
        }
        HEADER_FORMAT = {
            "font_name": FONT_NAME,
            "font_size": FONT_SIZE,
            "bg_color": "#DFDFFF",
            "bold": True,
            "left": 1,
            "right": 1,
        }
        NAN_FORMAT = {
            "font_name": FONT_NAME,
            "font_size": FONT_SIZE,
            "font_color": "silver",
            "top": 1,
            "left": 1,
            "bottom": 1,
            "right": 1,
        }

    @property
    def __nan_format_property(self) -> Dict:
        return self.format_table.get(self.TableFormat.NAN, self.default_format)

    @property
    def __cell_format_property(self) -> Dict:
        return self.format_table.get(self.TableFormat.CELL, self.default_format)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.default_format = self.Default.CELL_FORMAT
        self.format_table = {
            self.TableFormat.CELL: self.Default.CELL_FORMAT,
            self.TableFormat.HEADER: self.Default.HEADER_FORMAT,
            self.TableFormat.NAN: self.Default.NAN_FORMAT,
        }

        self.__col_cell_format_cache: Dict[int, Any] = {}
        self.__col_numprops_table: Dict[int, Dict] = {}

    def _open(self, workbook_path: str) -> None:
        self._workbook = ExcelWorkbookXlsx(workbook_path)

    def _write_header(self) -> None:
        if not self.is_write_header or typepy.is_empty_sequence(self.headers):
            return

        header_format_props = self.format_table.get(self.TableFormat.HEADER, self.default_format)
        header_format = self.__add_format(header_format_props)

        self.stream.write_row(
            row=self.first_header_row, col=0, data=self.headers, cell_format=header_format
        )
        for row in range(self.first_header_row, self.last_header_row):
            self.stream.write_row(
                row=row, col=0, data=[""] * len(self.headers), cell_format=header_format
            )

    def _write_cell(self, row: int, col: int, value_dp: DataProperty) -> None:
        base_props = dict(self.__cell_format_property)
        format_key = f"{col:d}_{value_dp.typecode.name:s}"

        if value_dp.typecode in [typepy.Typecode.INTEGER, typepy.Typecode.REAL_NUMBER]:
            num_props = self.__get_number_property(col)
            base_props.update(num_props)
            cell_format = self.__get_cell_format(format_key, base_props)

            try:
                self.stream.write_number(row, col, float(value_dp.data), cell_format)
                return
            except TypeError:
                pass

        if value_dp.typecode is typepy.Typecode.NAN:
            base_props = dict(self.__nan_format_property)

        cell_format = self.__get_cell_format(format_key, base_props)
        self.stream.write(row, col, value_dp.data, cell_format)

    def __get_number_property(self, col: int) -> Dict:
        if col in self.__col_numprops_table:
            return cast(Dict, self.__col_numprops_table.get(col))

        try:
            col_dp = self._column_dp_list[col]
        except KeyError:
            return {}

        if col_dp.typecode not in [typepy.Typecode.INTEGER, typepy.Typecode.REAL_NUMBER]:
            return {}

        num_props = {}
        if Integer(col_dp.minmax_decimal_places.max_value).is_type():
            float_digit = col_dp.minmax_decimal_places.max_value
            if float_digit > 0:
                num_props = {"num_format": "0.{:s}".format("0" * int(float_digit))}

        self.__col_numprops_table[col] = num_props

        return num_props

    def __get_cell_format(self, format_key, cell_props) -> Dict:
        cell_format = self.__col_cell_format_cache.get(format_key)
        if cell_format is not None:
            return cell_format

        # cache miss
        cell_format = self.__add_format(cell_props)
        self.__col_cell_format_cache[format_key] = cell_format

        return cell_format

    def __add_format(self, dict_property):
        return self.workbook.workbook.add_format(dict_property)

    def __set_cell_width(self):
        font_size = self.__cell_format_property.get("font_size")

        if not Integer(font_size).is_type():
            return

        for col_idx, col_dp in enumerate(self._column_dp_list):
            width = min(col_dp.ascii_char_width, self.MAX_CELL_WIDTH) * (font_size / 10.0) + 2
            self.stream.set_column(col_idx, col_idx, width=width)

    def _preprocess_table_property(self) -> None:
        super()._preprocess_table_property()

        self.__set_cell_width()

    def _postprocess(self) -> None:
        super()._postprocess()

        self.stream.autofilter(
            self.last_header_row, self.first_data_col, self.last_data_row, self.last_data_col
        )
        self.stream.freeze_panes(self.first_data_row, self.first_data_col)

        self.__col_cell_format_cache = {}
        self.__col_numprops_table = {}
