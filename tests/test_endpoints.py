import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.database import get_db
from app.models.user import User, UserRole


# ─── Setup ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user():
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "mohammed"
    user.email = "mohammed@test.com"
    user.role = UserRole.USER
    user.hashed_password = "hashed"
    return user


@pytest.fixture
def auth_headers(sample_user):
    from app.core.security import create_access_token
    token = create_access_token({"sub": sample_user.username, "role": sample_user.role})
    return {"Authorization": f"Bearer {token}"}


# ─── Auth Endpoint Tests ────────────────────────────────────────────────────────

class TestAuthEndpoints:

    def test_register_success(self, client, mock_db):
        mock_db.query().filter().first.return_value = None

        with patch("app.services.auth_services.hash_password", return_value="hashed"):
            response = client.post("/auth/register", json={
                "username": "newuser",
                "email": "new@test.com",
                "password": "password123"
            })

        assert response.status_code == 201

    def test_register_duplicate_username(self, client, mock_db, sample_user):
        mock_db.query().filter().first.return_value = sample_user

        response = client.post("/auth/register", json={
            "username": "mohammed",
            "email": "other@test.com",
            "password": "password123"
        })

        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    def test_login_success(self, client, mock_db, sample_user):
        mock_db.query().filter().first.return_value = sample_user

        with patch("app.services.auth_services.verify_password", return_value=True), \
             patch("app.services.auth_services.create_access_token", return_value="access"), \
             patch("app.services.auth_services.create_refresh_token", return_value="refresh"):

            response = client.post("/auth/login", json={
                "username": "mohammed",
                "password": "password123"
            })

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    def test_login_wrong_credentials(self, client, mock_db, sample_user):
        mock_db.query().filter().first.return_value = sample_user

        with patch("app.services.auth_services.verify_password", return_value=False):
            response = client.post("/auth/login", json={
                "username": "mohammed",
                "password": "wrong"
            })

        assert response.status_code == 401

    def test_me_authenticated(self, client, mock_db, sample_user, auth_headers):
        mock_db.query().filter().first.return_value = sample_user

        response = client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200

    def test_me_unauthenticated(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_logout(self, client):
        response = client.post("/auth/logout")
        assert response.status_code == 200


# ─── Query Endpoint Tests ───────────────────────────────────────────────────────

class TestQueryEndpoints:

    def test_ask_authenticated(self, client, mock_db, sample_user, auth_headers):
        mock_db.query().filter().first.return_value = sample_user

        with patch("app.api.routers.queries.rag_chain") as mock_chain:
            mock_chain.invoke.return_value = "La toux est causée par une infection virale."

            response = client.post("/queries/ask",
                json={"question": "causes de la toux"},
                headers=auth_headers
            )

        assert response.status_code == 200
        assert "answer" in response.json()

    def test_ask_unauthenticated(self, client):
        response = client.post("/queries/ask", json={"question": "test"})
        assert response.status_code == 401

    def test_ask_empty_question(self, client, mock_db, sample_user, auth_headers):
        mock_db.query().filter().first.return_value = sample_user

        response = client.post("/queries/ask",
            json={"question": ""},
            headers=auth_headers
        )
        # Should either return 422 (validation) or handle gracefully
        assert response.status_code in [200, 422]