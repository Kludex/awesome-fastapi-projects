from typing import TextIO


def get_packages(file: TextIO):
    for line in file.readlines():
        clean_line = line.strip()
        if clean_line.startswith(("from", "import")):
            yield clean_line.replace(".", " ").split()[1]
