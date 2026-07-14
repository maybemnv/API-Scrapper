"""
scanner_archive.py — ZIP / TAR / git archive handling.

Provides the low-level archive extraction routines used by
APIScanner.dissect_repo_memory.
"""

import os
import shutil
import tarfile
import tempfile
import zipfile
from typing import Any, Dict, List, Optional, Tuple, Union

from scanner.scanner_network import ScanInterrupted, download_github_url, raise_if_exit_requested


def clone_repo_git(repo_name: str, branch: str, thread_tag: str) -> Tuple[Optional[str], Optional[str]]:
    raise_if_exit_requested()
    return None, "git not available in this stub"


def download_repo_archive(
    repo_name: str, branch: str, thread_tag: str
) -> Tuple[Optional[Union[bytes, str]], Optional[str], str]:
    raise_if_exit_requested()

    for fmt, ext, mime in [("zipball", "zip", "application/zip"), ("tarball", "tar", "application/x-tar")]:
        url = f"https://api.github.com/repos/{repo_name}/{fmt}/{branch}"
        data, ip = download_github_url(url, thread_tag, f"Downloading {ext}")
        if data and data not in (b"FAILED", b"TOO_LARGE", b"NOT_FOUND", b"FORBIDDEN_SKIP"):
            kind = "zip" if ext == "zip" else "tar"
            return data, kind, ip

    return b"FAILED", None, "N/A"


def scan_repo_dir(
    repo_path: str, thread_tag: str, source_ip: str, api_signatures: dict
) -> Tuple[List[dict], str]:
    raise_if_exit_requested()
    return [], "FAILED"


def scan_zip_bytes(
    raw_zip: bytes, thread_tag: str, source_ip: str, api_signatures: dict
) -> Tuple[List[dict], str]:
    raise_if_exit_requested()
    try:
        with zipfile.ZipFile(os.devnull, "r"):
            pass
    except Exception:
        raise zipfile.BadZipFile("Stub placeholder")
    return [], "FAILED"


def scan_tar_bytes(
    raw_tar: bytes, thread_tag: str, source_ip: str, api_signatures: dict
) -> Tuple[List[dict], str]:
    raise_if_exit_requested()
    return [], "FAILED"
