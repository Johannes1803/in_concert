from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    sub: Mapped[str] = mapped_column(String(30))

    def insert(self, engine) -> int:
        """Inserts a user into the database and returns the user's id.
        param: engine: a SQLAlchemy engine
        return: the user's id
        """
        with Session(engine) as session:
            session.add(self)
            session.commit()
            session.refresh(self)
            return self.id
