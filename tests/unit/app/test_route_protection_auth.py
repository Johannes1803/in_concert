import pytest
from fastapi import Response
from fastapi.testclient import TestClient

from in_concert.app.app_factory import create_app


class TestApp:
    @pytest.fixture
    def response_obj(self):
        return Response()

    @pytest.fixture
    def client(self, settings_auth, engine):
        app = create_app(settings_auth, engine=engine)

        return TestClient(app)

    def test_get_private_route_non_logged_in_should_return_401(self, client):
        response = client.get("/private")
        assert response.status_code == 401

    def test_get_private_route_logged_in_should_return_200(self, client, bearer_token):
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client.get("/private")
        assert response.status_code == 200
