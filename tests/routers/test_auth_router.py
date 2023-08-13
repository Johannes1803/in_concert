import pytest
from fastapi.testclient import TestClient

from in_concert.routers.auth_router import create_router
from in_concert.settings import Auth0SettingsTest


class TestAuthRouter:
    @pytest.fixture
    def client(self):
        router = create_router(Auth0SettingsTest)
        return TestClient(router)

    def test_login(self, client):
        response = client.get("/login")
        assert response.status_code
