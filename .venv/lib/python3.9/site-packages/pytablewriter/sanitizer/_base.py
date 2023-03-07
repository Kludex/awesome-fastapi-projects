"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import abc
import re

from pathvalidate.error import ErrorReason, ValidationError
from typepy import is_null_string

from ._interface import NameSanitizer


def _preprocess(name: str) -> str:
    return name.strip()


class VarNameSanitizer(NameSanitizer):
    @abc.abstractproperty
    def _invalid_var_name_head_re(self):  # pragma: no cover
        pass

    @abc.abstractproperty
    def _invalid_var_name_re(self):  # pragma: no cover
        pass

    def validate(self) -> None:
        self._validate(self._value)

    def sanitize(self, replacement_text: str = "") -> str:
        var_name = self._invalid_var_name_re.sub(replacement_text, self._str)

        # delete invalid char(s) in the beginning of the variable name
        is_require_remove_head = any(
            [
                is_null_string(replacement_text),
                self._invalid_var_name_head_re.search(replacement_text) is not None,
            ]
        )

        if is_require_remove_head:
            var_name = self._invalid_var_name_head_re.sub("", var_name)
        else:
            match = self._invalid_var_name_head_re.search(var_name)
            if match is not None:
                var_name = match.end() * replacement_text + self._invalid_var_name_head_re.sub(
                    "", var_name
                )

        if not var_name:
            return ""

        try:
            self._validate(var_name)
        except ValidationError as e:
            if e.reason == ErrorReason.RESERVED_NAME and e.reusable_name is False:
                var_name += "_"

        return var_name

    def _validate(self, value: str) -> None:
        self._validate_null_string(value)

        unicode_var_name = _preprocess(value)

        if self._is_reserved_keyword(unicode_var_name):
            raise ValidationError(
                description=f"{unicode_var_name:s} is a reserved keyword by python",
                reason=ErrorReason.RESERVED_NAME,
                reusable_name=False,
                reserved_name=unicode_var_name,
            )

        match = self._invalid_var_name_re.search(unicode_var_name)
        if match is not None:
            raise ValidationError(
                description="invalid char found in the variable name: '{}'".format(
                    re.escape(match.group())
                ),
                reason=ErrorReason.INVALID_CHARACTER,
            )

        match = self._invalid_var_name_head_re.search(unicode_var_name)
        if match is not None:
            raise ValidationError(
                description="the first character of the variable name is invalid: '{}'".format(
                    re.escape(match.group())
                ),
                reason=ErrorReason.INVALID_CHARACTER,
            )
