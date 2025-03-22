import asyncio
from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from settings.database import get_async_session, get_async_redis

from . import service as service_core
from .models import User
from .tasks import send_email_active_account
from .dependencies import get_current_user
from .schemas import (CreateUserSchemas, GetUserSchemas, Token,
                      ChangeUsernameOrEmailSchema, ChangePasswordSchema)

router = APIRouter(
    tags=['core'],
    prefix='/core'
)

@router.get('/', response_model=List[GetUserSchemas], dependencies=[Depends(get_current_user)])
async def get_user_route(db: AsyncSession = Depends(get_async_session)):
    return await service_core.get_users(db)


@router.get('/{user_id}', response_model=GetUserSchemas)
async def get_user_by_id_route(
        user_id: int,
        db: AsyncSession = Depends(get_async_session)):
    return await service_core.get_user_by_id(db, user_id)


@router.post('/', response_model=GetUserSchemas)
async def create_user_route(
        user: Annotated[CreateUserSchemas, Form()],
        db: AsyncSession = Depends(get_async_session)
):
    user = await service_core.create_user(db, user)
    asyncio.create_task(send_email_active_account(user.id, user.email, user.username))
    return user


@router.get('/{uid}/{token}')
async def verify_email_route(
        uid: str,
        token: str,
        db: AsyncSession = Depends(get_async_session)
):
    return await service_core.verify_email(uid, db)


@router.post("/login")
async def login_for_access_token_route(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_async_session),
) -> Token:
    return await service_core.login_for_access_token(form_data, db)


@router.patch('/change_us_em', response_model=GetUserSchemas, dependencies=[Depends(get_current_user)])
async def pass_or_email_update_route(
        data: Annotated[ChangeUsernameOrEmailSchema, Form()],
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(get_current_user)
):
    return await service_core.change_username_email(data.username, data.email, user, db)


@router.patch('/change_password', dependencies=[Depends(get_current_user)])
async def change_password_route(
        data: Annotated[ChangePasswordSchema, Form()],
        db: AsyncSession = Depends(get_async_session),
        redis: AsyncSession = Depends(get_async_redis),
        user: User = Depends(get_current_user)
):
    return await service_core.change_password(password=data.password, new_password=data.new_password, user=user, db=db, redis=redis)


@router.post('/verify_password', dependencies=[Depends(get_current_user)], response_model=GetUserSchemas)
async def verify_password_route(
        code: Annotated[int, Form()],
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
        redis: AsyncSession = Depends(get_async_redis)
):
    return await service_core.verify_change_password(code, user, db, redis)

