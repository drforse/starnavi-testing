from datetime import datetime, date
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import db
from ..schemas import UserSchema
from ..auth import get_current_user
from ..dependecies import get_db_session
from ..schemas.likes import LikesSchema

router = APIRouter()


@router.get("/analytics", response_description="Get likes count", status_code=status.HTTP_200_OK,
            response_model=LikesSchema)
async def create_post(
        date_from: datetime | date | None = None,
        date_to: datetime | date | None = None,
        post_id: int = None,
        current_user: db.User = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_db_session),
):
    likes = db.LikesRepository(db_session)
    kwargs: dict[str, Any] = {"date_from": date_from, "date_to": date_to}
    if post_id is not None:
        kwargs.update(post_id=post_id)
    all_likes_count = await likes.count_aggregated_by_date(**kwargs)
    user_likes_count = await likes.count_aggregated_by_date(**kwargs, user_id=current_user.id)
    return {"all_likes_count": all_likes_count, "user_likes_count": user_likes_count}


@router.get(
    "/user/{user_id}",
    response_description="Get user info",
    status_code=status.HTTP_200_OK,
    response_model=UserSchema
)
async def user_info(
        user_id: int,
        current_user: db.models.User = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_db_session)
):
    if current_user.id == user_id:
        user = current_user
    else:
        users = db.UsersRepository(db_session)
        user = await users.get(id=user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="user not found")
    return user
