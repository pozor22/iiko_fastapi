from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from pydantic import EmailStr
from datetime import datetime, timedelta

from settings.base_model import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False, default=None)
    email: Mapped[EmailStr] = mapped_column(String(100), unique=True, index=True, nullable=False, default=None)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False, default=None)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    password_code: Mapped["PasswordCode"] = relationship("PasswordCode", back_populates="user")


class PasswordCode(Base):
    __tablename__ = 'password_codes'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, unique=True)
    code: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    user: Mapped["User"] = relationship("User", back_populates="password_code")

    def is_code_valid(self) -> bool:
        return datetime.now() - self.created_at <= timedelta(minutes=10)
