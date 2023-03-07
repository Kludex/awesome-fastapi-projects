import abc
import warnings
from typing import Any, Dict, Optional

import typepy

from ..._logger import logger
from ...sanitizer import sanitize_excel_sheet_name
from .._common import import_error_msg_template
from .._msgfy import to_error_message


class ExcelWorkbookInterface(metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def workbook(self):  # pragma: no cover
        pass

    @abc.abstractproperty
    def file_path(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def open(self, file_path: str) -> None:  # pragma: no cover
        pass

    @abc.abstractmethod
    def close(self) -> None:  # pragma: no cover
        pass

    @abc.abstractmethod
    def add_worksheet(self, worksheet_name):  # pragma: no cover
        pass


class ExcelWorkbook(ExcelWorkbookInterface):
    @property
    def workbook(self):
        return self._workbook

    @property
    def file_path(self) -> Optional[str]:
        return self._file_path

    def _clear(self) -> None:
        self._workbook = None
        self._file_path: Optional[str] = None
        self._worksheet_table: Dict[str, Any] = {}

    def __init__(self, file_path: str) -> None:
        self._clear()
        self._file_path = file_path

    def __del__(self) -> None:
        self.close()


class ExcelWorkbookXls(ExcelWorkbook):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)

        self.open(file_path)

    def open(self, file_path: str) -> None:
        try:
            import xlwt
        except ImportError:
            warnings.warn(import_error_msg_template.format("excel"))
            raise

        self._workbook = xlwt.Workbook()

    def close(self) -> None:
        if self.workbook is None:
            return

        try:
            self.workbook.save(self._file_path)
        except IndexError as e:
            logger.debug(to_error_message(e))

        self._clear()

    def add_worksheet(self, worksheet_name):
        worksheet_name = sanitize_excel_sheet_name(worksheet_name)

        if typepy.is_not_null_string(worksheet_name):
            if worksheet_name in self._worksheet_table:
                # the work sheet is already exists
                return self._worksheet_table.get(worksheet_name)
        else:
            sheet_id = 1
            while True:
                worksheet_name = f"Sheet{sheet_id:d}"
                if worksheet_name not in self._worksheet_table:
                    break
                sheet_id += 1

        worksheet = self.workbook.add_sheet(worksheet_name)
        self._worksheet_table[worksheet_name] = worksheet

        return worksheet


class ExcelWorkbookXlsx(ExcelWorkbook):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)

        self.open(file_path)

    def open(self, file_path: str) -> None:
        try:
            import xlsxwriter
        except ImportError:
            warnings.warn(import_error_msg_template.format("excel"))
            raise

        self._workbook = xlsxwriter.Workbook(file_path)

    def close(self) -> None:
        if self.workbook is None:
            return

        self._workbook.close()  # type: ignore
        self._clear()

    def add_worksheet(self, worksheet_name):
        worksheet_name = sanitize_excel_sheet_name(worksheet_name)

        if typepy.is_not_null_string(worksheet_name):
            if worksheet_name in self._worksheet_table:
                # the work sheet is already exists
                return self._worksheet_table.get(worksheet_name)
        else:
            worksheet_name = None

        worksheet = self.workbook.add_worksheet(worksheet_name)
        self._worksheet_table[worksheet_name] = worksheet

        return worksheet
