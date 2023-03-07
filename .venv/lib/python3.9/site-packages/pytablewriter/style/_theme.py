import importlib
import pkgutil
import re
from typing import Any, Dict, NamedTuple, Optional, Sequence

from .._logger import logger
from ..style import Cell, Style


try:
    from typing import Protocol
except ImportError:
    # typing.Protocol is only available starting from Python 3.8.
    from .._typing import Protocol  # type: ignore


KNOWN_PLUGINS = ("pytablewriter_altrow_theme",)


class StyleFilterFunc(Protocol):
    def __call__(self, cell: Cell, **kwargs: Dict[str, Any]) -> Optional[Style]:
        ...


class ColSeparatorStyleFilterFunc(Protocol):
    def __call__(
        self, left_cell: Optional[Cell], right_cell: Optional[Cell], **kwargs: Dict[str, Any]
    ) -> Optional[Style]:
        ...


class Theme(NamedTuple):
    style_filter: Optional[StyleFilterFunc]
    col_separator_style_filter: Optional[ColSeparatorStyleFilterFunc]


def list_themes() -> Sequence[str]:
    return list(load_ptw_plugins())


def load_ptw_plugins() -> Dict[str, Theme]:
    plugin_regexp = re.compile("^pytablewriter_.+_theme", re.IGNORECASE)
    discovered_plugins = {
        name: importlib.import_module(name)
        for _finder, name, _ispkg in pkgutil.iter_modules()
        if plugin_regexp.search(name) is not None
    }

    logger.debug(f"discovered_plugins: {list(discovered_plugins)}")

    return {
        theme: Theme(
            plugin.style_filter if hasattr(plugin, "style_filter") else None,
            plugin.col_separator_style_filter
            if hasattr(plugin, "col_separator_style_filter")
            else None,
        )
        for theme, plugin in discovered_plugins.items()
    }


def fetch_theme(plugin_name: str) -> Theme:
    loaded_themes = load_ptw_plugins()

    if plugin_name not in loaded_themes:
        err_msgs = [f"{plugin_name} theme is not installed."]

        if plugin_name in KNOWN_PLUGINS:
            err_msgs.append(f"try 'pip install {plugin_name}' to install the theme.")

        raise RuntimeError(" ".join(err_msgs))

    return loaded_themes[plugin_name]
