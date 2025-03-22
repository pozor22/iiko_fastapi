import jwt
import asyncio
import base64
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from pydantic import EmailStr

from settings import config as _config

from .tasks import send_email_active_account
from .schemas import CreateUserSchemas, Token
from .dependencies import pwd_context, get_user_by_username
from .models import User


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_users(db: AsyncSession):
    users = select(User)
    result = await db.execute(users)
    users = result.scalars().all()
    return users


async def get_user_by_id(db: AsyncSession, user_id: int):
    user = select(User).where(User.id == user_id)
    result = await db.execute(user)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


async def create_user(db: AsyncSession, user: CreateUserSchemas):
    hashed_password = get_password_hash(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError as e:
        await db.rollback()
        if "username" in str(e.orig):
            raise HTTPException(status_code=400, detail="Username already exists")
        elif "email" in str(e.orig):
            raise HTTPException(status_code=400, detail="Email already exists")
        else:
            raise HTTPException(status_code=400, detail="Unique constraint failed")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, _config.SECRET_KEY, algorithm=_config.ALGORITHM)
    return encoded_jwt


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def verify_email(uid: str, db: AsyncSession):
    try:
        user_id = int(base64.urlsafe_b64decode(uid).decode())
    except:
        raise HTTPException(status_code=400, detail="Invalid uid")
    user = await get_user_by_id(db, user_id)
    if not user.is_active:
        user.is_active = True
        await db.commit()
    return {"message": "Email verified"}


async def login_for_access_token(form_data, db):
    user = await authenticate_user(
        db=db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user, please, verify your email",
        )
    access_token_expires = timedelta(minutes=int(_config.ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


async def change_username_email(
        username: str | None,
        email: EmailStr | None,
        user: User,
        db: AsyncSession):
    if username and email:
        user.username = username
        user.email = email
        user.is_active = False
        asyncio.create_task(send_email_active_account(user.id, email, username))
        await db.commit()
        await db.refresh(user)
        return user
    elif username:
        user.username = username
        await db.commit()
        await db.refresh(user)
        return user
    elif email:
        user.email = email
        user.is_active = False
        asyncio.create_task(send_email_active_account(user.id, email, user.username))
        await db.commit()
        await db.refresh(user)
        return user
