import os
from tempfile import TemporaryDirectory
from typing import Generator, TextIO


def get_python_files(dir: TemporaryDirectory) -> Generator[TextIO, None, None]:
    for dirpath, _, filenames in os.walk(dir.name):
        for filename in filenames:
            if filename.endswith(".py"):
                yield open(os.sep.join([dirpath, filename]), "r")
