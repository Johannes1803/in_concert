"""Models representing the database tables."""
from sqlalchemy import Column, Engine, Integer, String
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


class Venue(Base):
    """A venue where a concert is held."""

    __tablename__ = "venues"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String(120), nullable=False)

    def insert(self, engine: Engine) -> int:
        """
        Insert a new venue into the database.

        param engine: The SQLAlchemy engine to use.
        return: The ID of the newly inserted venue.
        """
        with Session(engine) as session:
            session.add(self)
            session.commit()
            return int(self.id)
