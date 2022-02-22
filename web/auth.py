from datetime import timedelta, datetime

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db import UsersRepository, User
from utils import config
from web.dependecies import get_db_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(db_session: AsyncSession, username: str, password: str):
    repo = UsersRepository(db_session)
    user = await repo.get(username=username)
    if not user:
        return False
    if not verify_password(password, user.password.get_secret_value()):
        return False
    return user


def create_access_token(data: dict, expire_seconds: int):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=expire_seconds)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db_session: AsyncSession = Depends(get_db_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    repo = UsersRepository(db_session)
    user = await repo.get(username=username)
    if user is None:
        raise credentials_exception
    user.last_request_at = datetime.utcnow()
    await repo.update(user)
    return user
