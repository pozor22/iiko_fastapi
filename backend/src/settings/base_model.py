from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
