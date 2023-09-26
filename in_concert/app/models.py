from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    sub: Mapped[str] = mapped_column(String(30), index=True)

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
