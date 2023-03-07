"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from .__version__ import __author__, __copyright__, __email__, __license__, __version__
from ._common import convert_idx_to_alphabet
from ._constant import PatternMatch
from ._converter import to_value_matrix
from ._core import TableData
from ._logger import set_log_level, set_logger
from .error import DataError, InvalidHeaderNameError, InvalidTableNameError, NameValidationError
