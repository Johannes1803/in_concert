import pytest
from fastapi import FastAPI
from sqlalchemy.orm import Session

from in_concert.app.app_factory import create_app
from in_concert.app.models import Venue


class TestApp:
    @pytest.fixture
    def existing_venue_id(self, db_session: Session):
        with db_session:
            venue = Venue(
                name="venue name",
                street="venue street",
                city="venue city",
                state="venue state",
                zip_code=12345,
                phone=1234567890,
                website="venue website",
                image_link="venue image link",
                genres="venue genres",
                manager_id=1,
            )
            db_session.add(venue)
            db_session.commit()
            return venue.id

    def test_create_app_should_return_fast_api_app(self, settings_auth, engine):
        app = create_app(settings_auth, engine=engine)
        assert app
        assert isinstance(app, FastAPI)

    def test_get_home_route_should_return_200(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.content

    def test_post_user_should_create_user_in_db(
        self,
        client,
    ):
        response = client.post("/users", json={"id": "sub_id_123"})
        assert response.status_code == 201
        assert response.json()
        assert response.json()["id"] == "sub_id_123"

    def test_post_venue_manager_should_create_venue_manager_in_db(
        self,
        client,
    ):
        response = client.post("/venue_managers", json={"id": "sub_id_123"})
        assert response.status_code == 201
        assert response.json()
        assert response.json()["id"] == "sub_id_123"

    def test_post_venue_should_return_id_of_new_venue(self, client, bearer_token):
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client.post(
            "/venues",
            data={
                "name": "venue name",
                "street": "venue street",
                "city": "venue city",
                "state": "venue state",
                "zip_code": 12345,
                "phone": 1234567890,
                "website": "venue website",
                "image_link": "venue image link",
                "genres": "venue genres",
            },
        )
        assert response.status_code == 201
        assert response.json()
        assert response.json()["id"]

    def test_post_venue_should_create_venue_in_db(self, client, db_session: Session, bearer_token):
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client.post(
            "/venues",
            # response=response_obj,
            data={
                "name": "venue name",
                "street": "venue street",
                "city": "venue city",
                "state": "venue state",
                "zip_code": 12345,
                "phone": 1234567890,
                "website": "venue website",
                "image_link": "venue image link",
                "genres": "venue genres",
            },
        )
        venue_id = response.json()["id"]

        with db_session:
            venue = db_session.get(Venue, venue_id)
        assert venue

    def test_post_venue_with_missing_data_should_resend_form(self, client, bearer_token):
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client.post(
            "/venues",
            # missing name
            data={
                "street": "venue street",
                "city": "venue city",
                "state": "venue state",
                "zip_code": 12345,
                "phone": 1234567890,
                "website": "venue website",
                "image_link": "venue image link",
            },
        )
        assert response.status_code == 200

        html_response = response.content.decode(response.charset_encoding)
        # test previous user input is saved in form if validation fails
        assert 'value="venue street"' in html_response

    def test_get_venue_form_should_render_venue_form(self, client, bearer_token):
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client.get("/venues")
        assert response.status_code == 200
        assert response.content
        assert b"name" in response.content

    def test_delete_venue_should_delete_venue_in_db(
        self, client, existing_venue_id: int, db_session: Session, bearer_token
    ):
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        with db_session:
            venue = db_session.get(Venue, existing_venue_id)
        assert venue

        response = client.delete(f"/venues/{existing_venue_id}")
        assert response.status_code == 200

        with db_session:
            venue = db_session.get(Venue, existing_venue_id)
        assert not venue

    def test_delete_venue_should_return_404_if_venue_not_found(self, client, bearer_token):
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client.delete("/venues/123")
        assert response.status_code == 404
