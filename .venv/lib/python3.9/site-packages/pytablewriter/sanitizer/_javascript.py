"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import re
from typing import List, Pattern

from ._base import VarNameSanitizer


class JavaScriptVarNameSanitizer(VarNameSanitizer):
    __JS_RESERVED_KEYWORDS_ES6 = [
        "break",
        "case",
        "catch",
        "class",
        "const",
        "continue",
        "debugger",
        "default",
        "delete",
        "do",
        "else",
        "export",
        "extends",
        "finally",
        "for",
        "function",
        "if",
        "import",
        "in",
        "instanceof",
        "new",
        "return",
        "super",
        "switch",
        "this",
        "throw",
        "try",
        "typeof",
        "var",
        "void",
        "while",
        "with",
        "yield",
    ]
    __JS_RESERVED_KEYWORDS_FUTURE = [
        "enum",
        "implements",
        "interface",
        "let",
        "package",
        "private",
        "protected",
        "public",
        "static",
        "await",
        "abstract",
        "boolean",
        "byte",
        "char",
        "double",
        "final",
        "float",
        "goto",
        "int",
        "long",
        "native",
        "short",
        "synchronized",
        "throws",
        "transient",
        "volatile",
    ]
    __JS_BUILTIN_CONSTANTS = ["null", "true", "false"]

    __RE_INVALID_VAR_NAME = re.compile("[^a-zA-Z0-9_$]")
    __RE_INVALID_VAR_NAME_HEAD = re.compile("^[^a-zA-Z$]+")

    @property
    def reserved_keywords(self) -> List:
        return (
            self.__JS_RESERVED_KEYWORDS_ES6
            + self.__JS_RESERVED_KEYWORDS_FUTURE
            + self.__JS_BUILTIN_CONSTANTS
        )

    @property
    def _invalid_var_name_head_re(self) -> Pattern:
        return self.__RE_INVALID_VAR_NAME_HEAD

    @property
    def _invalid_var_name_re(self) -> Pattern:
        return self.__RE_INVALID_VAR_NAME


def validate_js_var_name(var_name: str) -> None:
    """
    :param str var_name: Name to validate.
    :raises pathvalidate.ValidationError (ErrorReason.INVALID_CHARACTER):
        If the ``var_name`` is invalid as a JavaScript identifier.
    :raises pathvalidate.ValidationError (ErrorReason.RESERVED_NAME):
        If the ``var_name`` is equals to
        `JavaScript reserved keywords
        <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Lexical_grammar#Keywords>`__.

    .. note::

        Currently, not supported unicode variable names.
    """

    JavaScriptVarNameSanitizer(var_name).validate()


def sanitize_js_var_name(var_name: str, replacement_text: str = "") -> str:
    """
    Make a valid JavaScript variable name from ``var_name``.

    To make a valid name:

    - Replace invalid characters for a JavaScript variable name within
      the ``var_name`` with the ``replacement_text``
    - Delete invalid chars for the beginning of the variable name
    - Append underscore (``"_"``) at the tail of the name if sanitized name
      is one of the JavaScript reserved names

    :JavaScriptstr filename: Name to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If ``var_name`` or ``replacement_text`` is invalid.

    :Example:
        :ref:`example-sanitize-var-name`

    .. note::
        Currently, not supported Unicode variable names.

    .. seealso::
        :py:func:`.validate_js_var_name`
    """

    return JavaScriptVarNameSanitizer(var_name).sanitize(replacement_text)
