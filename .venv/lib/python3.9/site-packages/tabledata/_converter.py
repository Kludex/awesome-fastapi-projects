"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from typing import Any, List, Sequence, Tuple

from .error import DataError


def to_value_matrix(headers: Sequence[str], value_matrix) -> List:
    if value_matrix is None:
        return []

    return [_to_row(headers, values, row_idx)[1] for row_idx, values in enumerate(value_matrix)]


def _to_row(headers: Sequence[str], values, row_idx: int) -> Tuple[int, Any]:
    if headers:
        try:
            values = values._asdict()
        except AttributeError:
            pass

        try:
            return (row_idx, [values.get(header) for header in headers])
        except (TypeError, AttributeError):
            pass

    if not isinstance(values, (tuple, list)):
        raise DataError(f"row must be a list or tuple: actual={type(values)}")

    return (row_idx, values)
