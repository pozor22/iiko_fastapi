from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import List, Annotated
from datetime import timedelta

from settings.database import get_async_session
from settings.config import ACCESS_TOKEN_EXPIRE_MINUTES

from .service import authenticate_user, create_access_token, get_password_hash
from .schemas import (CreateUserSchemas, GetUserSchemas,
                      Token)
from .models import User
from .dependencies import oauth2_scheme

router = APIRouter(
    tags=['core'],
    prefix='/core'
)

@router.get('/', response_model=List[GetUserSchemas], dependencies=[Depends(oauth2_scheme)])
async def get_user(db: AsyncSession = Depends(get_async_session)):
    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()
    return users


@router.post('/', response_model=GetUserSchemas)
async def create_user(
        user: Annotated[CreateUserSchemas, Form()],
        db: AsyncSession = Depends(get_async_session)
):
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


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_async_session),
) -> Token:
    user = await authenticate_user(
        db=db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

