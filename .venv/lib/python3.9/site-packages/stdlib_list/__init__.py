from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

# Import all the things that used to be in here for backwards-compatibility reasons
from .base import (
    stdlib_list,
    in_stdlib,
    get_canonical_version,
    short_versions,
    long_versions,
)
