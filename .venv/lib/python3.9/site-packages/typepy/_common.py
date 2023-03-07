import re
from typing import Any


ansi_escape = re.compile(r"(\x9b|\x1b\[)[0-?]*[ -\/]*[@-~]", re.IGNORECASE)
REGEXP_THOUSAND_SEP = re.compile(r"\d{1,3}(,\d{1,3})+")


def strip_ansi_escape(value: Any) -> str:
    return ansi_escape.sub("", value)


def remove_thousand_sep(value: str) -> str:
    if REGEXP_THOUSAND_SEP.search(value) is None:
        return value

    return value.replace(",", "")
