from sqlalchemy.orm import Session

from in_concert.app.models import User


def test_insert_user_should_add_user_to_db(db_session: Session) -> None:
    user = User(sub="oauth2|1234567890")

    user_id: int = user.insert(session=db_session)

    with db_session:
        user_from_db = db_session.query(User).get(user_id)
    assert user_from_db
    assert user_from_db.id
    assert user_from_db.sub == "oauth2|1234567890"
