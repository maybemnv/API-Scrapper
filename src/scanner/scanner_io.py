# ---------------------------------------------------------------------------------- #
#                            Part of the X3r0Day project.                            #
# ---------------------------------------------------------------------------------- #

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from . import scanner_state as state


def repo_identity(repo_name: str) -> str:
    return repo_name.lower().replace("https://github.com/", "").strip("/")


def dump_json_safely(filepath: str, data: Any) -> None:
    if state.DRY_RUN:
        return
    tmp = filepath + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        os.replace(tmp, filepath)
    except Exception:
        try:
            os.remove(tmp)
        except Exception:
            pass


def write_json_snapshot(data: Any, filepath: str) -> None:
    if state.DRY_RUN:
        return
    dump_json_safely(filepath, data)


def purge_old_entries(filepath: str, date_key: str = "date") -> int:
    max_age = state.MAX_AGE_DAYS
    if max_age is None:
        return 0
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            entries = json.load(fh)
    except Exception:
        return 0
    if not isinstance(entries, list):
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age)
    kept = []
    purged = 0
    for entry in entries:
        date_str = entry.get(date_key)
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                if dt < cutoff:
                    purged += 1
                    continue
            except (ValueError, TypeError):
                pass
        kept.append(entry)
    if purged > 0:
        dump_json_safely(filepath, kept)
    return purged
