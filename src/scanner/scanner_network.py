"""
scanner_network.py — HTTP download + proxy-fallback loop.

Provides network primitives used by the scanner to download
repository archives and commit patches.
"""

import time
from typing import Optional, Tuple


class ScanInterrupted(Exception):
    """Raised when the user requests a shutdown."""


def check_pause(thread_tag: str, action: str, ip: str) -> None:
    pass


def interruptible_sleep(seconds: float) -> bool:
    time.sleep(seconds)
    return True


def raise_if_exit_requested() -> None:
    pass


def download_github_url(
    url: str, thread_tag: str, action_label: str
) -> Tuple[Optional[bytes], str]:
    return None, "N/A"
