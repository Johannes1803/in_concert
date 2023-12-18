from typing import List

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


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
    image_link: Mapped[str] = mapped_column(String(), nullable=True)
    genres: Mapped[str] = mapped_column(String(30), nullable=True)
    manager_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    manager: Mapped["User"] = relationship(back_populates="venues")

    def __repr__(self):
        return f"<Venue {self.id} {self.name}>"


class User(Base):
    __tablename__ = "user_account"
    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    venues: Mapped[List[Venue]] = relationship(back_populates="manager")
    bands: Mapped[List["Band"]] = relationship(back_populates="manager")


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


class Band(Base):
    __tablename__ = "bands"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(30), nullable=True)
    zip_code: Mapped[int] = mapped_column(Integer(), nullable=True)
    state: Mapped[str] = mapped_column(String(30), nullable=True)
    website_link: Mapped[str] = mapped_column(String(120), nullable=True)
    image_link: Mapped[str] = mapped_column(String(), nullable=True)
    genres: Mapped[str] = mapped_column(String(120), nullable=True)
    manager_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    manager: Mapped["User"] = relationship(back_populates="bands")
