"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from typepy import Typecode

from ._align import Align


class AlignGetter:
    @property
    def typecode_align_table(self):
        raise NotImplementedError()

    @typecode_align_table.setter
    def typecode_align_table(self, x):
        self.__typecode_align_table = x

    def get_align_from_typecode(self, typecode):
        # pytype: disable=attribute-error
        return self.__typecode_align_table.get(typecode, self.default_align)
        # pytype: enable=attribute-error

    def __init__(self):
        self.typecode_align_table = {
            Typecode.STRING: Align.LEFT,
            Typecode.INTEGER: Align.RIGHT,
            Typecode.REAL_NUMBER: Align.RIGHT,
        }
        self.default_align = Align.LEFT


align_getter = AlignGetter()
