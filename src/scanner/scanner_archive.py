import io
import os
import tarfile
import zipfile
from typing import Callable, List, Optional

from . import scanner_state as state


def _should_skip_file(filename: str) -> bool:
    if state.EXCLUDE_EXTENSIONS:
        for ext in state.EXCLUDE_EXTENSIONS:
            if filename.lower().endswith(ext):
                return True
    if state.INCLUDE_EXTENSIONS:
        for ext in state.INCLUDE_EXTENSIONS:
            if filename.lower().endswith(ext):
                return False
        return True
    return False


def walk_tar(data: bytes, callback: Callable[[str, bytes], None]) -> None:
    buf = io.BytesIO(data)
    try:
        with tarfile.open(fileobj=buf, mode="r:*") as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                if _should_skip_file(member.name):
                    continue
                try:
                    file_data = tar.extractfile(member)
                    if file_data is not None:
                        callback(member.name, file_data.read())
                except Exception:
                    pass
    except tarfile.TarError:
        pass


def walk_zip(data: bytes, callback: Callable[[str, bytes], None]) -> None:
    buf = io.BytesIO(data)
    try:
        with zipfile.ZipFile(buf) as zf:
            for name in zf.namelist():
                if name.endswith("/"):
                    continue
                if _should_skip_file(name):
                    continue
                try:
                    callback(name, zf.read(name))
                except Exception:
                    pass
    except zipfile.BadZipFile:
        pass


def walk_archive(data: bytes, callback: Callable[[str, bytes], None]) -> None:
    walk_tar(data, callback)
    walk_zip(data, callback)
