from typing import Any, Callable

from populate.logger import log


def ignore_exceptions(func: Callable):
    def wrapper(*args: Any, **kwargs: Any):
        try:
            return func(*args, **kwargs)
        except Exception:
            log.exception(f"An exception has occurred on {func.__name__}")
            return None

    return wrapper
