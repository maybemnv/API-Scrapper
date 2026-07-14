import pytest


@pytest.mark.parametrize(
    "text,expected_repos",
    [
        ("https://github.com/owner/repo", [{"name": "owner/repo", "url": "https://github.com/owner/repo"}]),
        ("https://github.com/owner/repo.git", [{"name": "owner/repo", "url": "https://github.com/owner/repo"}]),
        ("Check https://github.com/foo/bar for details", [{"name": "foo/bar", "url": "https://github.com/foo/bar"}]),
        ("simple text with no URL", []),
        ("owner/repo with context github", [{"name": "owner/repo", "url": "https://github.com/owner/repo"}]),
    ],
)
def test_extract_repo_targets_regex(text, expected_repos):
    from shared.scanner_targets import extract_repo_targets_regex

    results = extract_repo_targets_regex(text)
    assert results == expected_repos


@pytest.mark.parametrize(
    "targets,expected_count",
    [
        ([{"name": "owner/repo"}, {"name": "owner/repo"}], 1),
        ([{"name": "owner/repo"}, {"name": "other/repo"}], 2),
        ([{"name": "owner/repo"}, {"name": "Owner/Repo"}], 1),
        ([], 0),
    ],
)
def test_dedupe_repo_targets(targets, expected_count):
    from shared.scanner_targets import dedupe_repo_targets

    results = dedupe_repo_targets(targets)
    assert len(results) == expected_count


@pytest.mark.parametrize(
    "name,expected",
    [
        ("owner/repo", True),
        ("user-name/project_name", True),
        ("u/p", True),
        ("/repo", False),
        ("owner/", False),
        ("sp ace/bad", False),
    ],
)
def test_is_valid_repo_name(name, expected):
    from shared.scanner_targets import is_valid_repo_name

    assert is_valid_repo_name(name) == expected


def test_dedupe_preserves_latest():
    from shared.scanner_targets import dedupe_repo_targets

    targets = [
        {"name": "owner/repo", "url": "https://github.com/owner/repo"},
        {"name": "owner/repo", "url": "https://github.com/owner/repo-v2"},
    ]
    results = dedupe_repo_targets(targets)
    assert len(results) == 1
    assert results[0]["url"] == "https://github.com/owner/repo-v2"


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Check owner/repo in github", [{"name": "owner/repo", "url": "https://github.com/owner/repo"}]),
        ("I need to scan foo/bar", []),
        ("Look at https://github.com/a/b", [{"name": "a/b", "url": "https://github.com/a/b"}]),
    ],
)
def test_extract_repo_targets_regex_context_sensitive(text, expected):
    from shared.scanner_targets import extract_repo_targets_regex

    results = extract_repo_targets_regex(text)
    assert results == expected
