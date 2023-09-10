from typing import Iterator

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from in_concert.app.models import Base, Venue


@pytest.fixture
def db_engine(settings_auth) -> Iterator[Engine]:
    engine = create_engine(settings_auth.db_connection_string, echo=True)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


def test_insert_venue_should_add_venue_to_db(db_engine: Engine) -> None:
    venue = Venue(name="Test Venue", city="Test City")

    venue_id: int = venue.insert(engine=db_engine)

    with Session(db_engine) as session:
        venue_from_db = session.query(Venue).get(venue_id)
    assert venue_from_db
    assert venue_from_db.id
    assert venue_from_db.name == "Test Venue"
