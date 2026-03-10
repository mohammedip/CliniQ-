import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.auth_services import register_user, login_user, refresh_tokens
from app.schemas.auth import UserRegister, UserLogin, RefreshRequest
from app.models.user import UserRole


# ─── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def sample_user():
    user = MagicMock()
    user.id = 1
    user.username = "mohammed"
    user.email = "mohammed@test.com"
    user.role = UserRole.USER
    user.hashed_password = "hashed_password_123"
    return user


# ─── Register Tests ────────────────────────────────────────────────────────────

class TestRegisterUser:

    def test_register_success(self, mock_db):
        mock_db.query().filter().first.return_value = None  # no existing user

        payload = UserRegister(
            username="newuser",
            email="new@test.com",
            password="password123"
        )

        with patch("app.services.auth_services.hash_password", return_value="hashed"):
            result = register_user(payload, mock_db)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_register_duplicate_username(self, mock_db, sample_user):
        mock_db.query().filter().first.return_value = sample_user  # user exists

        payload = UserRegister(
            username="mohammed",
            email="other@test.com",
            password="password123"
        )

        with pytest.raises(HTTPException) as exc:
            register_user(payload, mock_db)

        assert exc.value.status_code == 400
        assert "Username already taken" in exc.value.detail

    def test_register_duplicate_email(self, mock_db, sample_user):
        # First query (username) returns None, second (email) returns user
        mock_db.query().filter().first.side_effect = [None, sample_user]

        payload = UserRegister(
            username="newuser",
            email="mohammed@test.com",
            password="password123"
        )

        with pytest.raises(HTTPException) as exc:
            register_user(payload, mock_db)

        assert exc.value.status_code == 400
        assert "Email already registered" in exc.value.detail


# ─── Login Tests ───────────────────────────────────────────────────────────────

class TestLoginUser:

    def test_login_success(self, mock_db, sample_user):
        mock_db.query().filter().first.return_value = sample_user

        payload = UserLogin(username="mohammed", password="password123")

        with patch("app.services.auth_services.verify_password", return_value=True), \
             patch("app.services.auth_services.create_access_token", return_value="access_token"), \
             patch("app.services.auth_services.create_refresh_token", return_value="refresh_token"):

            result = login_user(payload, mock_db)

        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"
        assert result.token_type == "bearer"

    def test_login_wrong_password(self, mock_db, sample_user):
        mock_db.query().filter().first.return_value = sample_user

        payload = UserLogin(username="mohammed", password="wrongpassword")

        with patch("app.services.auth_services.verify_password", return_value=False):
            with pytest.raises(HTTPException) as exc:
                login_user(payload, mock_db)

        assert exc.value.status_code == 401
        assert "Invalid username or password" in exc.value.detail

    def test_login_user_not_found(self, mock_db):
        mock_db.query().filter().first.return_value = None

        payload = UserLogin(username="ghost", password="password123")

        with pytest.raises(HTTPException) as exc:
            login_user(payload, mock_db)

        assert exc.value.status_code == 401


# ─── Refresh Token Tests ───────────────────────────────────────────────────────

class TestRefreshTokens:

    def test_refresh_success(self, mock_db, sample_user):
        mock_db.query().filter().first.return_value = sample_user

        payload = RefreshRequest(refresh_token="valid_refresh_token")

        with patch("app.services.auth_services.decode_token", return_value={"type": "refresh", "sub": "mohammed"}), \
             patch("app.services.auth_services.create_access_token", return_value="new_access"), \
             patch("app.services.auth_services.create_refresh_token", return_value="new_refresh"):

            result = refresh_tokens(payload, mock_db)

        assert result.access_token == "new_access"
        assert result.refresh_token == "new_refresh"

    def test_refresh_invalid_token(self, mock_db):
        payload = RefreshRequest(refresh_token="bad_token")

        with patch("app.services.auth_services.decode_token", return_value=None):
            with pytest.raises(HTTPException) as exc:
                refresh_tokens(payload, mock_db)

        assert exc.value.status_code == 401
        assert "Invalid or expired refresh token" in exc.value.detail

    def test_refresh_wrong_token_type(self, mock_db):
        payload = RefreshRequest(refresh_token="access_token_used_as_refresh")

        with patch("app.services.auth_services.decode_token", return_value={"type": "access", "sub": "mohammed"}):
            with pytest.raises(HTTPException) as exc:
                refresh_tokens(payload, mock_db)

        assert exc.value.status_code == 401

    def test_refresh_user_not_found(self, mock_db):
        mock_db.query().filter().first.return_value = None

        payload = RefreshRequest(refresh_token="valid_token")

        with patch("app.services.auth_services.decode_token", return_value={"type": "refresh", "sub": "ghost"}):
            with pytest.raises(HTTPException) as exc:
                refresh_tokens(payload, mock_db)

        assert exc.value.status_code == 401
        assert "User not found" in exc.value.detail