import pytest


@pytest.mark.parametrize(
    "query,expected",
    [
        ("how many keys are there", True),
        ("count the number of api keys", True),
        ("what categories are available", True),
        ("which types of keys are supported", True),
        ("list all keys", False),
        ("show me openai keys", False),
        ("give me aws keys", False),
    ],
)
def test_is_summary_query(query, expected):
    from shared.category_routing import is_summary_query

    assert is_summary_query(query) == expected


@pytest.mark.parametrize(
    "query,must_contain",
    [
        ("openai keys", "OpenAI API Key (Legacy)"),
        ("aws access key", "AWS Access Key ID"),
        ("github token", "GitHub Classic PAT"),
        ("slack webhook url", "Slack Webhook"),
    ],
)
def test_infer_categories_from_query(query, must_contain):
    from shared.category_routing import infer_categories_from_query

    result = infer_categories_from_query(query)
    assert must_contain in result


def test_infer_all_categories():
    from shared.category_routing import infer_categories_from_query

    result = infer_categories_from_query("show all api keys")
    assert len(result) >= 5


def test_infer_returns_list():
    from shared.category_routing import infer_categories_from_query

    result = infer_categories_from_query("random gibberish zzz")
    assert isinstance(result, list)
    assert len(result) >= 0


@pytest.mark.parametrize(
    "query,categories,expected_substring",
    [
        ("", [], "selected categories"),
        ("show everything", [], "selected categories"),
    ],
)
def test_describe_scope_no_categories(query, categories, expected_substring):
    from shared.category_routing import describe_scope

    result = describe_scope(query, categories)
    assert expected_substring in result


    @pytest.mark.parametrize(
        "query,expected",
        [
            ("available categories", True),
            ("how many", True),
            ("list categories", False),
            ("show all the api keys", False),
        ],
    )
    def test_summary_query_true_for_list_categories(query, expected):
        from shared.category_routing import is_summary_query

        assert is_summary_query(query) == expected


def test_normalize_categories():
    from shared.api_signatures import API_SIGNATURE_CATEGORIES
    from shared.category_routing import normalize_categories

    cats = ["Slack Webhook", "AWS Access Key ID", "OpenAI API Key (Legacy)"]
    result = normalize_categories(cats)
    assert sorted(cats) == sorted(result)
    assert len(result) == 3
    expected_order = [c for c in API_SIGNATURE_CATEGORIES if c in cats]
    assert result == expected_order


def test_normalize_categories_deduplicates():
    from shared.category_routing import normalize_categories

    result = normalize_categories(["AWS Access Key ID", "AWS Access Key ID"])
    assert len(result) == 1
