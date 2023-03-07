from __future__ import print_function, absolute_import

import os
import pkgutil
import sys

try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache

long_versions = ["2.6.9", "2.7.9", "3.2.6", "3.3.6", "3.4.3", "3.5", "3.6",
                 "3.7", "3.8", "3.9"]

short_versions = [".".join(x.split(".")[:2]) for x in long_versions]


def get_canonical_version(version):

    if version in long_versions:
        version = ".".join(version.split(".")[:2])
    elif version not in short_versions:
        raise ValueError("No such version: {}".format(version))

    return version


def stdlib_list(version=None):
    """
    Given a ``version``, return a ``list`` of names of the Python Standard
    Libraries for that version. These names are obtained from the Sphinx inventory
    file (used in :py:mod:`sphinx.ext.intersphinx`).

    :param str|None version: The version (as a string) whose list of libraries you want
    (one of ``"2.6"``, ``"2.7"``, ``"3.2"``, ``"3.3"``, ``"3.4"``, or ``"3.5"``).
    If not specified, the current version of Python will be used.

    :return: A list of standard libraries from the specified version of Python
    :rtype: list
    """

    version = get_canonical_version(version) if version is not None else '.'.join(
        str(x) for x in sys.version_info[:2])

    module_list_file = os.path.join("lists", "{}.txt".format(version))

    data = pkgutil.get_data("stdlib_list", module_list_file).decode()

    result = [y for y in [x.strip() for x in data.splitlines()] if y]

    return result


@lru_cache(maxsize=16)
def _stdlib_list_with_cache(version=None):
    """Internal cached version of `stdlib_list`"""
    return stdlib_list(version=version)


@lru_cache(maxsize=256)
def in_stdlib(module_name, version=None):
    """
    Return a ``bool`` indicating if module ``module_name`` is in the list of stdlib
    symbols for python version ``version``. If ``version`` is ``None`` (default), the
    version of current python interpreter is used.

    Note that ``True`` will be returned for built-in modules too, since this project
    considers they are part of stdlib. See :issue:21.

    It relies on ``@lru_cache`` to cache the stdlib list and query results for similar
    calls. Therefore it is much more efficient than ``module_name in stdlib_list()``
    especially if you wish to perform multiple checks.

    :param str|None module_name: The module name (as a string) to query for.
    :param str|None version: The version (as a string) whose list of libraries you want
    (one of ``"2.6"``, ``"2.7"``, ``"3.2"``, ``"3.3"``, ``"3.4"``, or ``"3.5"``).
    If not specified, the current version of Python will be used.

    :return: A bool indicating if the given module name is part of standard libraries
    for the specified version of Python.
    :rtype: list
    """
    ref_list = _stdlib_list_with_cache(version=version)
    return module_name in ref_list
