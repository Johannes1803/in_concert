from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    def insert(self, session: Session) -> int:
        """Inserts an entry into the database and returns the entry's id.
        param: session: a SQLAlchemy session
        return: the entry's id
        """
        with session:
            with session.begin():
                session.add(self)
            return self.id


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    street: Mapped[str] = mapped_column(String(30))
    city: Mapped[str] = mapped_column(String(30))
    zip_code: Mapped[int] = mapped_column(Integer())
    state: Mapped[str] = mapped_column(String(30))
    phone: Mapped[int] = mapped_column(Integer())
    website: Mapped[str] = mapped_column(String(30), nullable=True)
    image_link: Mapped[str] = mapped_column(String(30), nullable=True)
    genres: Mapped[str] = mapped_column(String(30), nullable=True)

    def __repr__(self):
        return f"<Venue {self.id} {self.name}>"


class User(Base):
    __tablename__ = "user_account"
    id: Mapped[str] = mapped_column(String(30), primary_key=True)


def delete_db_entry(session: Session, id: int, model_class: Base) -> int:
    """Delete an entry from the database.

    :param session: alchemy orm session
    :param id: id of the entry to delete
    :param model_class: table to delete
    :raises KeyError: if the entry does not exist in the database
    :return: the id of the deleted entry
    """
    with session, session.begin():
        db_entry = session.get(model_class, id)
        if not db_entry:
            raise KeyError(f"No {model_class.__name__} with id {id} exists in the database.")
        else:
            db_entry_id = db_entry.id
            session.delete(db_entry)

    return db_entry_id
