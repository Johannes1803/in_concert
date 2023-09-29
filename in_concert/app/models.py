from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
