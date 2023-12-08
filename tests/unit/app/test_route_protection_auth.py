from unittest import mock

import pytest
import pytest_asyncio
from fastapi import Response
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from in_concert.app.models import Venue
from in_concert.settings import AppSettings


class TestApp:
    """Test all possible cases of route protection.

    classic RBAC:
    - non-logged in user => 401
    - logged in user with insufficient scope => 403
    - logged in user with sufficient scope => 200/201

    fine-grained access control:
    - logged in user with insufficient fine-grained access control permissions => 403
    - logged in user with sufficient fine-grained access control permissions => 200/201
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

    @pytest_asyncio.fixture
    async def existing_venue_id_with_fga_permissions(
        self, db_session: Session, app_settings_test: AppSettings, client: TestClient
    ) -> int:
        venue_id: int = 101
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
                id=venue_id,
            )
            db_session.add(venue)
            db_session.commit()

        user = f"{app_settings_test.client_id}@clients"
        client.app.user_oauth_integrator.user_authorizer.get_current_user_id = mock.AsyncMock(return_value=user)
        await client.app.user_oauth_integrator.user_authorizer_fga.add_permissions(
            request={}, relations=["can_delete", "can_update"], object_type="venue", object_id=venue_id
        )

        yield venue_id

        # await client.app.user_oauth_integrator.user_authorizer_fga.remove_permissions(
        #     request={}, relations=["can_delete"], object_type="venue", object_id=venue_id
        # )

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

    @pytest.mark.asyncio
    def test_fga_sufficient_scope_should_return_200(
        self, client, existing_venue_id_with_fga_permissions: int, db_session: Session, bearer_token
    ):
        """
        Test positive case fine grained access control.

        Test that a logged in user with sufficient fine-grained acccess control permissions gets a 200 response when
        trying to access a private route.
        """
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        with db_session:
            venue = db_session.get(Venue, existing_venue_id_with_fga_permissions)
        assert venue

        response = client.delete(f"/venues/{existing_venue_id_with_fga_permissions}")
        assert response.status_code == 200

    def test_fga_scope_permissions_removed_on_object_deletion(
        self, client, existing_venue_id_with_fga_permissions: int, db_session: Session, bearer_token
    ):
        """
        Test fga scope permissions are removed on object deletion.
        """
        client.cookies = {"access_token": f'Bearer {bearer_token["access_token"]}'}
        with db_session:
            venue = db_session.get(Venue, existing_venue_id_with_fga_permissions)
        assert venue

        _ = client.delete(f"/venues/{existing_venue_id_with_fga_permissions}")
