import abc


class TextWriterInterface(metaclass=abc.ABCMeta):
    """
    Interface class for writing texts.
    """

    @abc.abstractmethod
    def write_null_line(self):  # pragma: no cover
        pass


class IndentationInterface(metaclass=abc.ABCMeta):
    """
    Interface class for indentation methods.
    """

    @abc.abstractmethod
    def set_indent_level(self, indent_level):  # pragma: no cover
        pass

    @abc.abstractmethod
    def inc_indent_level(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def dec_indent_level(self):  # pragma: no cover
        pass
