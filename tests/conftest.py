import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture
def sample_signatures_path():
    return str(Path(__file__).resolve().parent / "fixtures" / "sample_signatures.json")


@pytest.fixture
def mock_signatures(sample_signatures_path):
    from shared.signature_loader import build_sigs

    return build_sigs(include_heroku=True, pth=sample_signatures_path)


@pytest.fixture
def mock_signatures_no_heroku(sample_signatures_path):
    from shared.signature_loader import build_sigs

    return build_sigs(include_heroku=False, pth=sample_signatures_path)


@pytest.fixture
def mock_leaked_keys():
    return [
        {
            "name": "owner/repo",
            "url": "https://github.com/owner/repo",
            "leaks": [
                {"file": "config.py", "line": 10, "type": "OpenAI API Key (Legacy)", "secret": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "entropy": 4.5}
            ],
        }
    ]


@pytest.fixture
def tmp_output_dir(tmp_path):
    d = tmp_path / "output"
    d.mkdir()
    return d


@pytest.fixture
def mock_ai_client(monkeypatch):
    def fake_post(url, key, pay, tmo):
        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {"choices": [{"message": {"content": '{"mode":"query"}'}}]}

        return FakeResponse()

    monkeypatch.setattr("shared.requests_compat.requests.post", fake_post)
    return {"api_url": "https://api.groq.com/openai/v1/chat/completions", "model": "test-model", "timeout": 5, "max_retries": 1}
