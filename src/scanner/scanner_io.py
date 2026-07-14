"""
scanner_io.py — Atomic JSON persistence.

Provides safe file I/O helpers used by the scanner to persist
scan results without corruption.
"""

import json


def dump_json_safely(path: str, data: dict) -> None:
    pass


def ensure_json_list_file(path: str) -> None:
    pass


def remove_from_queue(repo_name: str) -> None:
    pass
