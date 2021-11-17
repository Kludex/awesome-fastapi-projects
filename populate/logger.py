import logging

from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="%(timestamp)s - %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger("rich")
