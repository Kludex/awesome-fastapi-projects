from enum import Enum, unique


@unique
class LineBreakHandling(Enum):
    NOP = 0
    REPLACE = 1
    ESCAPE = 2
