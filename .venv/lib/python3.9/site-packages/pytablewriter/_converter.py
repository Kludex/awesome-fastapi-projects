"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import re


def strip_quote(text: str, value: str) -> str:
    re_replace = re.compile(f"[\"']{value:s}[\"']", re.MULTILINE)

    return re_replace.sub(value, text)
