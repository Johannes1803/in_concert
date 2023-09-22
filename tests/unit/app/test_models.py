from typing import Iterator

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from in_concert.app.models import Base, User


@pytest.fixture
def db_engine(settings_auth) -> Iterator[Engine]:
    engine = create_engine(settings_auth.db_connection_string.get_secret_value())
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


def test_insert_user_should_add_user_to_db(db_engine: Engine) -> None:
    user = User(sub="oauth2|1234567890")

    user_id: int = user.insert(engine=db_engine)

    with Session(db_engine) as session:
        user_from_db = session.query(User).get(user_id)
    assert user_from_db
    assert user_from_db.id
    assert user_from_db.sub == "oauth2|1234567890"
