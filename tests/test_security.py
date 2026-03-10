import pytest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


# ─── Password Tests ────────────────────────────────────────────────────────────

class TestPasswordHashing:

    def test_hash_password_returns_string(self):
        hashed = hash_password("mypassword")
        assert isinstance(hashed, str)

    def test_hash_is_not_plain_text(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"

    def test_verify_correct_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_same_password_different_hashes(self):
        # bcrypt generates different salts each time
        hash1 = hash_password("mypassword")
        hash2 = hash_password("mypassword")
        assert hash1 != hash2


# ─── JWT Token Tests ───────────────────────────────────────────────────────────

class TestJWTTokens:

    def test_create_access_token(self):
        token = create_access_token({"sub": "mohammed", "role": "user"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        token = create_refresh_token({"sub": "mohammed", "role": "user"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        token = create_access_token({"sub": "mohammed"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "mohammed"
        assert payload["type"] == "access"

    def test_decode_refresh_token(self):
        token = create_refresh_token({"sub": "mohammed"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "mohammed"
        assert payload["type"] == "refresh"

    def test_decode_invalid_token(self):
        result = decode_token("this.is.not.a.valid.token")
        assert result is None

    def test_decode_empty_token(self):
        result = decode_token("")
        assert result is None

    def test_access_and_refresh_tokens_are_different(self):
        data = {"sub": "mohammed"}
        access = create_access_token(data)
        refresh = create_refresh_token(data)
        assert access != refresh

    def test_token_type_is_correct(self):
        access = create_access_token({"sub": "mohammed"})
        refresh = create_refresh_token({"sub": "mohammed"})

        access_payload = decode_token(access)
        refresh_payload = decode_token(refresh)

        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"