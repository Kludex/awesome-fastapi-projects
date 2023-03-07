import platform

from .__version__ import __author__, __copyright__, __email__, __license__, __version__
from ._const import AnsiBGColor, AnsiFGColor, AnsiStyle
from ._truecolor import Color, RGBTuple, tcolor


if platform.system() == "Windows":
    from ctypes import windll  # type: ignore

    # https://docs.microsoft.com/en-us/windows/console/getstdhandle
    STD_OUTPUT_HANDLE = -11

    # https://docs.microsoft.com/en-us/windows/console/setconsolemode
    ENABLE_PROCESSED_OUTPUT = 1
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 4

    windll.kernel32.SetConsoleMode(
        windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE),
        ENABLE_PROCESSED_OUTPUT | ENABLE_VIRTUAL_TERMINAL_PROCESSING,
    )
