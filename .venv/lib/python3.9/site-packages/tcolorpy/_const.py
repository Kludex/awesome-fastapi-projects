from enum import Enum, unique


CSI = "\033["
RESET = CSI + "0m"


@unique
class AnsiStyle(Enum):
    BOLD = 1
    DIM = 2
    ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    INVERT = 7
    STRIKE = 9


class AnsiFGColor(Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    LIGHTBLACK = 90
    LIGHTRED = 91
    LIGHTGREEN = 92
    LIGHTYELLOW = 93
    LIGHTBLUE = 94
    LIGHTMAGENTA = 95
    LIGHTCYAN = 96
    LIGHTWHITE = 97
    LBLACK = 90
    LRED = 91
    LGREEN = 92
    LYELLOW = 93
    LBLUE = 94
    LMAGENTA = 95
    LCYAN = 96
    LWHITE = 97


class AnsiBGColor(Enum):
    BLACK = 40
    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    WHITE = 47
    LIGHTBLACK = 100
    LIGHTRED = 101
    LIGHTGREEN = 102
    LIGHTYELLOW = 103
    LIGHTBLUE = 104
    LIGHTMAGENTA = 105
    LIGHTCYAN = 106
    LIGHTWHITE = 107
    LBLACK = 100
    LRED = 101
    LGREEN = 102
    LYELLOW = 103
    LBLUE = 104
    LMAGENTA = 105
    LCYAN = 106
    LWHITE = 107
