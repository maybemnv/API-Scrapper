import pytest


def test_sig_names(sample_signatures_path):
    from shared.signature_loader import sig_names

    names = sig_names(pth=sample_signatures_path)
    assert "OpenAI API Key (Legacy)" in names
    assert "Heroku API Key" in names
    assert len(names) == 6


@pytest.mark.parametrize("include_heroku,expected_count", [(True, 6), (False, 5)])
def test_build_sigs_heroku_filtering(sample_signatures_path, include_heroku, expected_count):
    from shared.signature_loader import build_sigs

    sigs = build_sigs(include_heroku=include_heroku, pth=sample_signatures_path)
    assert len(sigs) == expected_count
    if include_heroku:
        assert "Heroku API Key" in sigs
    else:
        assert "Heroku API Key" not in sigs


def test_pattern_compilation(sample_signatures_path):
    from shared.signature_loader import build_sigs

    sigs = build_sigs(pth=sample_signatures_path)
    openai_pat = sigs["OpenAI API Key (Legacy)"]
    assert openai_pat.match("sk-" + "a" * 48)
    assert not openai_pat.match("bad-key")


def test_file_not_found_raises():
    from shared.signature_loader import _load

    with pytest.raises(FileNotFoundError):
        _load(pth="nonexistent.json")


@pytest.mark.parametrize(
    "name,text,expected",
    [
        ("OpenAI API Key (Legacy)", "sk-" + "a" * 48, True),
        ("GitHub Classic PAT", "ghp_" + "a" * 36, True),
        ("AWS Access Key ID", "AKIA" + "A" * 16, True),
        ("OpenAI API Key (Legacy)", "bad-key", False),
        ("GitHub Classic PAT", "not-a-token", False),
    ],
)
def test_specific_patterns(sample_signatures_path, name, text, expected):
    from shared.signature_loader import build_sigs

    sigs = build_sigs(pth=sample_signatures_path)
    pat = sigs.get(name)
    assert pat is not None
    assert bool(pat.match(text)) == expected
