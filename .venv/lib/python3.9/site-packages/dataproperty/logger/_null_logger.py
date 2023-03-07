class NullLogger:
    level_name = None

    def remove(self, handler_id=None):  # pragma: no cover
        pass

    def add(self, sink, **kwargs):  # pragma: no cover
        pass

    def disable(self, name):  # pragma: no cover
        pass

    def enable(self, name):  # pragma: no cover
        pass

    def critical(self, __message, *args, **kwargs):  # pragma: no cover
        pass

    def debug(self, __message, *args, **kwargs):  # pragma: no cover
        pass

    def error(self, __message, *args, **kwargs):  # pragma: no cover
        pass

    def exception(self, __message, *args, **kwargs):  # pragma: no cover
        pass

    def info(self, __message, *args, **kwargs):  # pragma: no cover
        pass

    def log(self, __level, __message, *args, **kwargs):  # pragma: no cover
        pass

    def success(self, __message, *args, **kwargs):  # pragma: no cover
        pass

    def trace(self, __message, *args, **kwargs):  # pragma: no cover
        pass

    def warning(self, __message, *args, **kwargs):  # pragma: no cover
        pass
