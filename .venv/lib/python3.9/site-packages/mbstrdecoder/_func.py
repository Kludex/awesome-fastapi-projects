"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import os
import stat
from errno import EBADF, ENOENT, ENOTDIR
from typing import Optional, Union

from ._binary_ext_checker import is_binary_ext_path


def is_fifo(file_path: Union[int, bytes, str]) -> bool:
    try:
        return stat.S_ISFIFO(os.stat(file_path).st_mode)
    except OSError as e:
        if e.errno not in (ENOENT, ENOTDIR, EBADF):
            raise

        return False
    except ValueError:
        return False


def to_codec_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None

    return name.lower().replace("-", "_")


def detect_file_encoding(file_path) -> Optional[str]:
    from chardet.universaldetector import UniversalDetector

    if not os.path.isfile(file_path) or is_binary_ext_path(file_path) or is_fifo(file_path):
        return None

    detector = UniversalDetector()
    READ_SIZE = 4 * 1024

    try:
        with open(file_path, mode="rb") as f:
            while True:
                binary = f.read(READ_SIZE)
                if not binary:
                    break

                detector.feed(binary)
                if detector.done:
                    break
    except OSError:
        return None
    finally:
        detector.close()

    return to_codec_name(detector.result.get("encoding"))
