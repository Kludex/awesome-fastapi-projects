"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from enum import Enum
from typing import Optional, Type

import dataproperty
from pathvalidate import replace_symbol
from tabledata._core import TableData


def quote_datetime_formatter(value) -> str:
    return f'"{value.strftime(dataproperty.DefaultValue.DATETIME_FORMAT):s}"'


def dateutil_datetime_formatter(value) -> str:
    return 'dateutil.parser.parse("{:s}")'.format(
        value.strftime(dataproperty.DefaultValue.DATETIME_FORMAT)
    )


def dumps_tabledata(value: TableData, format_name: str = "rst_grid_table", **kwargs) -> str:
    """
    :param tabledata.TableData value: Tabular data to dump.
    :param str format_name:
        Dumped format name of tabular data.
        Available formats are described in
        :py:meth:`~pytablewriter.TableWriterFactory.create_from_format_name`

    :Example:
        .. code:: python

            >>> dumps_tabledata(value)
            .. table:: sample_data

                ======  ======  ======
                attr_a  attr_b  attr_c
                ======  ======  ======
                     1     4.0  a
                     2     2.1  bb
                     3   120.9  ccc
                ======  ======  ======
    """

    from ._factory import TableWriterFactory

    if not value:
        raise TypeError("value must be a tabledata.TableData instance")

    writer = TableWriterFactory.create_from_format_name(format_name)

    for attr_name, attr_value in kwargs.items():
        setattr(writer, attr_name, attr_value)

    writer.from_tabledata(value)

    return writer.dumps()


def dump_tabledata(value, format_name="rst_grid_table", **kwargs):
    # deprecated: alias to dumps_tabledata()
    return dumps_tabledata(value, format_name, **kwargs)


def normalize_enum(
    value, enum_class: Type[Enum], validate: bool = True, default: Optional[Enum] = None
):
    if value is None:
        return default

    if isinstance(value, enum_class):
        return value

    try:
        return enum_class[replace_symbol(value.strip(), "_").upper()]
    except AttributeError:
        if validate:
            raise TypeError(f"value must be a {enum_class} or a str: actual={type(value)}")
    except KeyError:
        if validate:
            raise ValueError(
                "invalid valid found: expected={}, actual={}".format(
                    "/".join(item.name for item in enum_class), value
                )
            )

    return value
