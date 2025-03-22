from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime
from pydantic import EmailStr
from datetime import datetime

from settings.base_model import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False, default=None)
    email: Mapped[EmailStr] = mapped_column(String(100), unique=True, index=True, nullable=False, default=None)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False, default=None)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
