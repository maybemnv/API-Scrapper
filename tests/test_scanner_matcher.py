import pytest


class TestNormalizeMatch:
    def test_non_firebase_passthrough(self):
        from shared.scanner_matcher import normalize_match

        class FakeHit:
            def group(self, _=0):
                return "sk-test-key"

        result = normalize_match("OpenAI API Key (Legacy)", "some text", FakeHit())
        assert result == "sk-test-key"

    def test_firebase_expands_url(self):
        from shared.scanner_matcher import normalize_match

        match_text = "https://myapp.firebaseio.com"

        class FakeHit:
            def group(self, _=0):
                return match_text

            def end(self):
                return len(match_text)

        text = "https://myapp.firebaseio.com/.json"
        result = normalize_match("Firebase Database URL", text, FakeHit())
        assert result == "https://myapp.firebaseio.com/.json"
        assert ".json" in result

    def test_firebase_missing_json_returns_none(self):
        from shared.scanner_matcher import normalize_match

        class FakeHit:
            def group(self, _=0):
                return "https://myapp.firebaseio.com"

            def end(self):
                return 0

        text = "https://myapp.firebaseio.com/somepath"
        result = normalize_match("Firebase Database URL", text, FakeHit())
        assert result is None


class TestPhVal:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("", True),
            ("   ", True),
            ("${VAR}", True),
            ("$(VAR)", True),
            ("{{ placeholder }}", True),
            ("redacted", True),
            ("***", True),
            ("xxxxxx", True),
            ("test", True),
            ("password", True),
            ("abc123", True),
            ("my_key_123", False),
            ("12345678", True),
            ("qwerty", True),
            ("real-secret-value-123", False),
            ("abcdefgh", True),
            ("somepassword", True),
            ("valid-key-abc-def", False),
        ],
    )
    def test_ph_val_detection(self, value, expected):
        from shared.scanner_matcher import _ph_val

        assert _ph_val(value) == expected


class TestFalsePositiveMatch:
    @pytest.mark.parametrize(
        "api_name,secret,filename,line_data,raw_text,expected",
        [
            ("OpenAI API Key (Legacy)", "sk-" + "a" * 48, "test.py", "", "", True),
            ("OpenAI API Key (Legacy)", "sk-" + ("a" * 48), "test.py", "", "", True),
            ("OpenAI API Key (Legacy)", "sk-live-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0", "test.py", "", "lots of text here", False),
            ("Google API/GCP Key", "AIza" + "a" * 35, "firebase.html", "apiKey: AIza...", "firebase config with apiKey", True),
            ("OpenAI API Key (Legacy)", "sk-proj-" + "a1b2c3d4e5f6g7h8i9j0k1l2" * 2, "config.py", "", "", False),
        ],
    )
    def test_false_positive(self, api_name, secret, filename, line_data, raw_text, expected):
        from shared.scanner_matcher import _is_false_positive_match

        result = _is_false_positive_match(api_name, secret, filename, line_data, raw_text)
        assert result == expected


class TestShannonEntropy:
    @pytest.mark.parametrize(
        "data,expected",
        [
            ("", 0.0),
            ("aaaa", 0.0),
            ("abcd", 2.0),
        ],
    )
    def test_entropy_values(self, data, expected):
        from shared.scanner_matcher import shannon_entropy

        result = shannon_entropy(data)
        assert result == expected

    def test_high_entropy_long_string(self):
        from shared.scanner_matcher import shannon_entropy

        ent = shannon_entropy("sk-" + "a1b2c3d4e5f6g7h8i9j0" * 3)
        assert ent > 3.0


class TestPkBlocks:
    @pytest.mark.parametrize(
        "text,expected_types",
        [
            (
                "-----BEGIN RSA PRIVATE KEY-----\n" + ("a1b2c3d4e5f6g7h8i9j0" * 12) + "\n" + ("k1l2m3n4o5p6q7r8s9t0" * 10) + "\n-----END RSA PRIVATE KEY-----",
                ["Private Key (RSA)"],
            ),
            (
                "-----BEGIN EC PRIVATE KEY-----\n" + ("u1v2w3x4y5z6A7B8C9D0" * 12) + "\n" + ("E1F2G3H4I5J6K7L8M9N0" * 10) + "\n-----END EC PRIVATE KEY-----",
                ["Private Key (EC)"],
            ),
            (
                "some normal text without keys",
                [],
            ),
        ],
    )
    def test_pk_block_detection(self, text, expected_types):
        from shared.scanner_matcher import _pk_blocks

        results = _pk_blocks(text)
        types = [r[0] for r in results]
        assert types == expected_types


class TestSbJwtType:
    @pytest.mark.parametrize(
        "token,expected",
        [
            ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJvbGUiOiJzZXJ2aWNlX3JvbGUiLCJyZWYiOiJhYmNkZWYifQ.dummy", "Supabase Service Role Key (JWT)"),
            ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJvbGUiOiJhbm9uIiwicmVmIjoiYWJjZGVmIn0.dummy", None),
            ("not-a-jwt", None),
        ],
    )
    def test_sb_jwt_type(self, token, expected):
        from shared.scanner_matcher import _sb_jwt_type

        result = _sb_jwt_type(token)
        assert result == expected
