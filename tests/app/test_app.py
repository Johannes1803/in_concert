import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from in_concert.app.app_factory import create_app


class TestApp:
    @pytest.fixture
    def client(self, settings_auth):
        app = create_app(settings_auth)
        return TestClient(app)

    def test_get_app_should_return_fast_api_app(self, settings_auth):
        app = create_app(settings_auth)
        assert app
        assert isinstance(app, FastAPI)

    def test_get_home_route_should_return_200(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()

    def test_get_private_route_non_logged_in_should_return_401(self, client):
        response = client.get("/private")
        assert response.status_code == 401

    def test_get_private_route_logged_in_should_return_200(self, client, bearer_token):
        response = client.get("/private", cookies={"access_token": f'Bearer {bearer_token["access_token"]}'})
        assert response.status_code == 200
