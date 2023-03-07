"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from typing import List

import dataproperty
from mbstrdecoder import MultiByteStrDecoder

from ._null_logger import NullLogger


MODULE_NAME = "pytablewriter"

try:
    from loguru import logger

    logger.disable(MODULE_NAME)
except ImportError:
    logger = NullLogger()


def set_logger(is_enable: bool, propagation_depth: int = 1) -> None:
    if is_enable:
        logger.enable(MODULE_NAME)
    else:
        logger.disable(MODULE_NAME)

    if propagation_depth <= 0:
        return

    dataproperty.set_logger(is_enable, propagation_depth - 1)

    try:
        import simplesqlite

        simplesqlite.set_logger(is_enable, propagation_depth - 1)
    except ImportError:
        pass

    try:
        import pytablereader

        pytablereader.set_logger(is_enable, propagation_depth - 1)
    except ImportError:
        pass


def set_log_level(log_level):
    # deprecated
    logger.disable(MODULE_NAME)


class WriterLogger:
    @property
    def logger(self):
        return self.__logger

    def __init__(self, writer) -> None:
        self.__writer = writer
        self.__logger = logger

        self.logger.debug(f"created WriterLogger: format={writer.format_name}")

    def __enter__(self):
        self.logging_start_write()
        return self

    def __exit__(self, *exc):
        self.logging_complete_write()
        return False

    def logging_start_write(self) -> None:
        log_entry_list = [
            self.__get_format_name_message(),
            self.__get_table_name_message(),
            f"headers={self.__writer.headers}",
        ]

        try:
            log_entry_list.append(f"rows={len(self.__writer.value_matrix)}")
        except (TypeError, AttributeError):
            log_entry_list.append("rows=NaN")

        log_entry_list.append(self.__get_typehint_message())
        log_entry_list.extend(self.__get_extra_log_entry_list())

        self.logger.debug("start write table: {}".format(", ".join(log_entry_list)))

    def logging_complete_write(self) -> None:
        log_entry_list = [self.__get_format_name_message(), self.__get_table_name_message()]
        log_entry_list.extend(self.__get_extra_log_entry_list())

        self.logger.debug("complete write table: {}".format(", ".join(log_entry_list)))

    def __get_format_name_message(self) -> str:
        return f"format={self.__writer.format_name:s}"

    def __get_table_name_message(self) -> str:
        if self.__writer.table_name:
            table_name = MultiByteStrDecoder(self.__writer.table_name).unicode_str
        else:
            table_name = ""

        return f"table-name='{table_name}'"

    def __get_extra_log_entry_list(self) -> List[str]:
        if self.__writer._iter_count is None:
            return []

        return [f"iteration={self.__writer._iter_count}/{self.__writer.iteration_length}"]

    def __get_typehint_message(self) -> str:
        try:
            return "type-hints={}".format(
                [type_hint(None).typename for type_hint in self.__writer.type_hints]
            )
        except (TypeError, AttributeError):
            return "type-hints=[]"
