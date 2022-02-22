from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import db
from utils import config
from ..auth import authenticate_user, create_access_token, get_password_hash
from ..dependecies import get_db_session
from ..schemas import UserSchema, UserCreateSchema, TokenSchema

router = APIRouter()


@router.post("/sign_up", response_description="Sign Up", status_code=status.HTTP_200_OK,
             response_model=UserSchema, response_model_exclude_none=True)
async def sign_up(
        user_create: UserCreateSchema = Depends(UserCreateSchema.as_form),
        db_session: AsyncSession = Depends(get_db_session)
):
    if not user_create.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="password cannot be empty")
    repo = db.UsersRepository(db_session)
    in_db = await repo.get(username=user_create.username)
    if in_db is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="user with this username already exists")
    hashed_pwd = get_password_hash(user_create.password.get_secret_value())
    user_create_db = db.UserCreate(**user_create.dict(exclude={"password"}), password=hashed_pwd)
    user = await repo.create(user_create_db)
    return user


@router.post("/token", status_code=status.HTTP_200_OK, response_model=TokenSchema)
async def create_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db_session: AsyncSession = Depends(get_db_session)
):
    user = await authenticate_user(db_session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.username}, config.ACCESS_TOKEN_EXPIRE_SECONDS)
    users = db.UsersRepository(db_session)
    user.last_login_at = datetime.utcnow()
    user.last_request_at = user.last_login_at
    await users.update(user)
    return {"access_token": access_token, "token_type": "bearer"}
