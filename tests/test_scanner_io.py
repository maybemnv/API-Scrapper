import json
import os

import pytest


def test_ensure_json_list_file_creates(tmp_path):
    from scanner.scanner_io import ensure_json_list_file

    fp = str(tmp_path / "test_queue.json")
    ensure_json_list_file(fp)
    assert os.path.exists(fp)
    with open(fp, "r") as f:
        data = json.load(f)
    assert data == []


def test_ensure_json_list_file_exists(tmp_path):
    from scanner.scanner_io import ensure_json_list_file

    fp = str(tmp_path / "existing.json")
    with open(fp, "w") as f:
        json.dump([{"test": "data"}], f)
    ensure_json_list_file(fp)
    with open(fp, "r") as f:
        data = json.load(f)
    assert data == [{"test": "data"}]


def test_dump_json_safely_writes_valid_json(tmp_path):
    from scanner.scanner_io import dump_json_safely

    fp = str(tmp_path / "leaks.json")
    blob = {"name": "owner/repo", "url": "https://github.com/owner/repo", "leaks": []}
    dump_json_safely(fp, blob)
    with open(fp, "r") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "owner/repo"


def test_dump_json_safely_updates_existing(tmp_path):
    from scanner.scanner_io import dump_json_safely

    fp = str(tmp_path / "leaks.json")
    blob1 = {"name": "owner/repo", "leaks": [{"secret": "key1"}]}
    blob2 = {"name": "owner/repo", "leaks": [{"secret": "key2"}]}
    dump_json_safely(fp, blob1)
    dump_json_safely(fp, blob2)
    with open(fp, "r") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["leaks"][0]["secret"] == "key2"


def test_remove_from_queue_non_existent(tmp_path):
    from scanner.scanner_io import remove_from_queue

    import scanner.scanner_state as state

    original = state.QUEUE_JSON
    try:
        state.QUEUE_JSON = str(tmp_path / "nonexistent_queue.json")
        remove_from_queue("owner/repo")
    finally:
        state.QUEUE_JSON = original


def test_remove_from_queue_removes_entry(tmp_path):
    from scanner.scanner_io import remove_from_queue

    import scanner.scanner_state as state

    qp = str(tmp_path / "queue.json")
    with open(qp, "w") as f:
        json.dump([{"name": "keep/repo"}, {"name": "remove/me"}, {"name": "keep/too"}], f)
    original = state.QUEUE_JSON
    try:
        state.QUEUE_JSON = qp
        remove_from_queue("remove/me")
        with open(qp, "r") as f:
            data = json.load(f)
        names = [e["name"] for e in data]
        assert "remove/me" not in names
        assert len(data) == 2
    finally:
        state.QUEUE_JSON = original
