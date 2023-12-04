import pytest
from fastapi import FastAPI
from sqlalchemy.orm import Session

from in_concert.app.app_factory import AppFactory
from in_concert.app.models import Venue


class TestApp:
    """Test all routes.

    Route protection is tested in test_route_protection_auth.py. Here, we test the routes themselves.
    """

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

    def test_create_app_should_return_fast_api_app(self, app_settings_test, engine):
        app_factory = AppFactory()
        app_factory.configure(app_settings_test)
        app = app_factory.create_app(app_settings_test, engine=engine)
        assert app
        assert isinstance(app, FastAPI)

    def test_get_home_route_should_return_200(self, client_no_auth_checks):
        response = client_no_auth_checks.get("/")
        assert response.status_code == 200
        assert response.content

    def test_post_user_should_create_user_in_db(
        self,
        client_no_auth_checks,
    ):
        response = client_no_auth_checks.post("/users", json={"id": "sub_id_123"})
        assert response.status_code == 201
        assert response.json()
        assert response.json()["id"] == "sub_id_123"

    def test_post_venue_manager_should_create_venue_manager_in_db(
        self,
        client_no_auth_checks,
    ):
        response = client_no_auth_checks.post("/venue_managers", json={"id": "sub_id_123"})
        assert response.status_code == 201
        assert response.json()
        assert response.json()["id"] == "sub_id_123"

    def test_post_venue_should_return_id_of_new_venue(self, client_no_auth_checks, bearer_token):
        client_no_auth_checks.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client_no_auth_checks.post(
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

    def test_post_venue_should_create_venue_in_db(self, client_no_auth_checks, db_session: Session, bearer_token):
        client_no_auth_checks.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client_no_auth_checks.post(
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

    def test_post_venue_with_missing_data_should_resend_form(self, client_no_auth_checks, bearer_token):
        client_no_auth_checks.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client_no_auth_checks.post(
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

    def test_get_venue_form_should_render_venue_form(self, client_no_auth_checks, bearer_token):
        client_no_auth_checks.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client_no_auth_checks.get("/venues")
        assert response.status_code == 200
        assert response.content
        assert b"name" in response.content

    def test_delete_venue_should_delete_venue_in_db(
        self, client_no_auth_checks, existing_venue_id: int, db_session: Session, bearer_token
    ):
        client_no_auth_checks.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        with db_session:
            venue = db_session.get(Venue, existing_venue_id)
        assert venue

        response = client_no_auth_checks.delete(f"/venues/{existing_venue_id}")
        assert response.status_code == 200

        with db_session:
            venue = db_session.get(Venue, existing_venue_id)
        assert not venue

    def test_delete_venue_should_return_404_if_venue_not_existing(self, client_no_auth_checks, bearer_token):
        client_no_auth_checks.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client_no_auth_checks.delete("/venues/123")
        assert response.status_code == 404

    def test_list_venue_should_return_venue_list(self, client_no_auth_checks, existing_venue_id: int):
        response = client_no_auth_checks.get("/list_venues")
        assert response.status_code == 200
        assert response.content

    def test_get_venue_should_return_venue(self, client_no_auth_checks, existing_venue_id: int):
        response = client_no_auth_checks.get(f"/venues/{existing_venue_id}")
        assert response.status_code == 200
        assert response.content
