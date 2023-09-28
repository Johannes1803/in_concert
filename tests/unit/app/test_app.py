import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from in_concert.app.app_factory import create_app


class TestApp:
    @pytest.fixture
    def client(self, settings_auth, engine):
        app = create_app(settings_auth, engine=engine)
        return TestClient(app)

    def test_create_app_should_return_fast_api_app(self, settings_auth, engine):
        app = create_app(settings_auth, engine=engine)
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
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client.get("/private")
        assert response.status_code == 200

    def test_post_user_should_create_user_in_db(self, client):
        response = client.post("/users", json={"id": "sub_id_123"})
        assert response.status_code == 201
        assert response.json()
        assert response.json()["id"] == "sub_id_123"
