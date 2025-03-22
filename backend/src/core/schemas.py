from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str


class UserSchemas(UserBase):
    id: int
    is_active: bool = True


class CreateUserSchemas(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        from_attribute = True


class GetUserSchemas(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attribute = True


class ResponseLoginUserSchema(BaseModel):
    access: str
    user: GetUserSchemas

    class Config:
        from_attribute = True


class LoginUserSchema(BaseModel):
    username: str
    password: str

    class Config:
        from_attribute = True


class ChangeUsernameOrEmailSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

    class Config:
        from_attribute = True
