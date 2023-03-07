"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import dataproperty

from ._null_logger import NullLogger


MODULE_NAME = "tabledata"

try:
    from loguru import logger

    logger.disable(MODULE_NAME)
except ImportError:
    logger = NullLogger()


def set_logger(is_enable, propagation_depth=1):
    if is_enable:
        logger.enable(MODULE_NAME)
    else:
        logger.disable(MODULE_NAME)

    if propagation_depth <= 0:
        return

    dataproperty.set_logger(is_enable, propagation_depth - 1)


def set_log_level(log_level):
    # deprecated
    return
