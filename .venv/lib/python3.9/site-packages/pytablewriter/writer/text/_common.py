from decimal import Decimal
from typing import Any

from dataproperty import DataProperty
from typepy import Typecode


def bool_to_str(value) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"

    return value


def serialize_dp(dp: DataProperty) -> Any:
    if dp.typecode in (Typecode.REAL_NUMBER, Typecode.INFINITY, Typecode.NAN) and isinstance(
        dp.data, Decimal
    ):
        return float(dp.data)

    if dp.typecode == Typecode.DATETIME:
        return dp.to_str()

    return dp.data
