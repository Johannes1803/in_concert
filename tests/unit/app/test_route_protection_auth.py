import pytest
from fastapi import Response
from sqlalchemy.orm import Session

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

    @pytest.fixture
    def existing_venue_id_with_delete_permissions(self, db_session: Session):
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
                id=100,
            )
            db_session.add(venue)
            db_session.commit()
            return venue.id

    @pytest.fixture
    def response_obj(self):
        return Response()

    def test_get_private_route_non_logged_in_should_return_401(self, client):
        """Test that a non-logged in user gets a 401 response when trying to access a private route."""
        response = client.get("/private")
        assert response.status_code == 401

    # ToDo:
    # def test_get_route_insufficient_scope_should_return_403(self, client, bearer_token):
    #       pass

    def test_get_route_sufficient_scope_should_return_200(self, client, bearer_token):
        """
        Test that a logged in user with sufficient scope gets a 200 response when trying to access a private route.
        """
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        response = client.get("/private")
        assert response.status_code == 200

    def test_fga_insufficient_scope_should_return_403(
        self, client, existing_venue_id: int, db_session: Session, bearer_token
    ):
        """
        Test negative case fine grained access control.

        Test that a logged in user with insufficient fine-grained acccess control permissions gets a 403 response when
        trying to access a private route.
        """
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        with db_session:
            venue = db_session.get(Venue, existing_venue_id)
        assert venue

        response = client.delete(f"/venues/{existing_venue_id}")
        assert response.status_code == 403

    def test_fga_sufficient_scope_should_return_200(
        self, client, existing_venue_id_with_delete_permissions: int, db_session: Session, bearer_token
    ):
        """
        Test negative case fine grained access control.

        Test that a logged in user with insufficient fine-grained acccess control permissions gets a 403 response when
        trying to access a private route.
        """
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        with db_session:
            venue = db_session.get(Venue, existing_venue_id_with_delete_permissions)
        assert venue

        response = client.delete(f"/venues/{existing_venue_id_with_delete_permissions}")
        assert response.status_code == 200
