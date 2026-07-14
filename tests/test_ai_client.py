import pytest


class TestJsonFromText:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ('{"mode":"query"}', {"mode": "query"}),
            ('{"key": "value"}', {"key": "value"}),
            ('Sure! {"mode":"query"}', {"mode": "query"}),
            ('Here is the result: {"count": 5}', {"count": 5}),
            ('{"nested": {"inner": true}}', {"nested": {"inner": True}}),
        ],
    )
    def test_valid_json(self, text, expected):
        from shared.ai_client import _json_from_text

        assert _json_from_text(text) == expected

    def test_malformed_json_raises(self):
        from shared.ai_client import _json_from_text

        with pytest.raises(Exception):
            _json_from_text("this is not json at all")

    def test_empty_string_raises(self):
        from shared.ai_client import _json_from_text

        with pytest.raises(Exception):
            _json_from_text("")

    def test_wrapped_with_leading_text(self):
        from shared.ai_client import _json_from_text

        result = _json_from_text('Here is the JSON: {"mode":"query","target":"owner/repo"}')
        assert result == {"mode": "query", "target": "owner/repo"}

    def test_json_with_trailing_text(self):
        from shared.ai_client import _json_from_text

        result = _json_from_text('{"mode":"query"} I hope this helps')
        assert result == {"mode": "query"}


class TestBuildMsgs:
    def test_basic_message_list(self):
        from shared.ai_client import build_msgs

        msgs = build_msgs("You are a helpful assistant", "Scan this repo")
        assert len(msgs) == 2
        assert msgs[0] == {"role": "system", "content": "You are a helpful assistant"}
        assert msgs[1] == {"role": "user", "content": "Scan this repo"}

    def test_with_history(self):
        from shared.ai_client import build_msgs

        history = [{"role": "assistant", "content": "Previous response"}]
        msgs = build_msgs("System prompt", "User query", history=history)
        assert len(msgs) == 3
        assert msgs[0] == {"role": "system", "content": "System prompt"}
        assert msgs[1] == {"role": "assistant", "content": "Previous response"}
        assert msgs[2] == {"role": "user", "content": "User query"}

    def test_empty_history(self):
        from shared.ai_client import build_msgs

        msgs = build_msgs("sys", "user", history=[])
        assert len(msgs) == 2


class TestRememberExchange:
    def test_appends_exchange(self):
        from shared.ai_client import remember_exchange

        history = [{"role": "system", "content": "sys"}]
        remember_exchange(history, "user text", "assistant text")
        assert len(history) == 3
        assert history[-2]["role"] == "user"
        assert history[-2]["content"] == "user text"
        assert history[-1]["role"] == "assistant"
        assert history[-1]["content"] == "assistant text"

    def test_trims_history(self):
        from shared.ai_client import remember_exchange

        from shared.ai_client import MAX_HISTORY_MESSAGES

        history = [{"role": "user", "content": f"msg{i}"} for i in range(MAX_HISTORY_MESSAGES)]
        remember_exchange(history, "new user", "new assistant")
        assert len(history) <= MAX_HISTORY_MESSAGES

    def test_none_history_does_nothing(self):
        from shared.ai_client import remember_exchange

        remember_exchange(None, "user", "assistant")
