from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    address: Mapped[str] = mapped_column(String(30))
    state: Mapped[str] = mapped_column(String(30))
    zip_code: Mapped[str] = mapped_column(Integer())
    phone: Mapped[int] = mapped_column(Integer())
    website: Mapped[str] = mapped_column(String(30))
    image_link: Mapped[str] = mapped_column(String(30))
    genres: Mapped[str] = mapped_column(String(30))

    def __repr__(self):
        return f"<Venue {self.id} {self.name}>"


class User(Base):
    __tablename__ = "user_account"
    id: Mapped[str] = mapped_column(String(30), primary_key=True)

    def insert(self, session: Session) -> int:
        """Inserts a user into the database and returns the user's id.
        param: session: a SQLAlchemy session
        return: the user's id
        """
        with session:
            session.add(self)
            session.commit()
            session.refresh(self)
            return self.id
