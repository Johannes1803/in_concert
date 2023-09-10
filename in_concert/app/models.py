from sqlalchemy import Column, Engine, Integer, String
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


class Venue(Base):
    __tablename__ = "venues"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String(120), nullable=False)

    def insert(self, engine: Engine) -> int:
        with Session(engine) as session:
            session.add(self)
            session.commit()
            return int(self.id)
