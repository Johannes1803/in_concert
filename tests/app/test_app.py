import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from in_concert.app.app_factory import create_app


class TestApp:
    @pytest.fixture
    def client(self):
        app = create_app()
        return TestClient(app)

    def test_get_app_should_return_fast_api_app(self):
        app = create_app()
        assert app
        assert isinstance(app, FastAPI)

    def test_get_home_route_should_return_200(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()
