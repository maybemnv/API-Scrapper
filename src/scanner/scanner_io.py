import json
import os
import tempfile
import time
from typing import Any, Generator


def repo_identity(repo_name: str) -> str:
    return repo_name.strip().lower()


def write_json_snapshot(payload: list, filename: str) -> None:
    directory = os.path.dirname(os.path.abspath(filename)) or "."
    file_prefix = f".{os.path.basename(filename)}."
    fd, tmp = tempfile.mkstemp(prefix=file_prefix, suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=4)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, filename)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def dump_json_safely(payload: Any, filename: str) -> None:
    write_json_snapshot(payload if isinstance(payload, list) else [payload], filename)


def stream_json_entries(filepath: str) -> Generator[dict, None, None]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(content):
        while idx < len(content) and content[idx].isspace():
            idx += 1
        if idx >= len(content):
            break
        if content[idx] == "[":
            idx += 1
            continue
        if content[idx] == "]":
            break
        obj, end = decoder.raw_decode(content, idx)
        yield obj
        idx = end
        if idx < len(content) and content[idx] == ",":
            idx += 1
