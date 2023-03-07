"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import enum


@enum.unique
class PatternMatch(enum.Enum):
    OR = 0
    AND = 1
