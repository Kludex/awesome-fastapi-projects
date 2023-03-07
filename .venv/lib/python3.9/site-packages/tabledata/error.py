"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


class NameValidationError(ValueError):
    """
    Exception raised when a name is invalid.
    """


class InvalidTableNameError(NameValidationError):
    """
    Exception raised when a table name is invalid.
    """


class InvalidHeaderNameError(NameValidationError):
    """
    Exception raised when a table header name is invalid.
    """


class DataError(ValueError):
    """
    Exception raised when data is invalid as tabular data.
    """
