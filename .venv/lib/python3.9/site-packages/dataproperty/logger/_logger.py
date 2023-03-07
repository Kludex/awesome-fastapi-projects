"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from ._null_logger import NullLogger


MODULE_NAME = "dataproperty"

try:
    from loguru import logger

    logger.disable(MODULE_NAME)
except ImportError:
    logger = NullLogger()  # type: ignore


def set_logger(is_enable, propagation_depth=1):
    if is_enable:
        logger.enable(MODULE_NAME)
    else:
        logger.disable(MODULE_NAME)


def set_log_level(log_level):
    # deprecated
    logger.disable(MODULE_NAME)
    return
