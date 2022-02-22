from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import db.models
from db.models import LikeCreate
from db.repositories import PostsRepository
from db.repositories.mysql import LikesRepository
from ..schemas import PostCreateSchema, PostSchema
from ..auth import get_current_user
from ..dependecies import get_db_session

router = APIRouter()


@router.post("/posts", response_description="Create post",
             status_code=status.HTTP_201_CREATED,
             response_model=PostSchema, response_model_exclude_none=True)
async def create_post(
        *,
        fields: str = None,
        post_create: PostCreateSchema,
        current_user: db.models.User = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_db_session),
):
    chains = set(fields.split(",")) if fields else set()
    db_post_create = db.models.PostCreate(**post_create.dict(), user_id=current_user.id)
    try:
        result = await PostsRepository(db_session, chains).create(db_post_create)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except RecursionError:
        raise HTTPException(400, detail="fields contain recursion")
    return result


@router.post("/posts/{post_id}/like", response_description="Like post", status_code=status.HTTP_200_OK)
async def like_post(
        post_id: int,
        current_user: db.models.User = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_db_session)
):
    posts = PostsRepository(db_session, {"user"})
    likes = LikesRepository(db_session, {"user", "post"})
    post = await posts.get(id=post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="post not found")
    like = await likes.get(user_id=current_user.id, post_id=post.id)
    if like is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="already liked")
    like = LikeCreate(user_id=current_user.id, post_id=post.id)
    await likes.create(like)
    await posts.update(post)


@router.delete("/posts/{post_id}/like", response_description="Unlike post", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_post(
        post_id: int,
        current_user: db.models.User = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_db_session)
):
    posts = PostsRepository(db_session, {"user"})
    post = await posts.get(id=post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="post not found")

    likes = LikesRepository(db_session, {"user", "post"})
    like = await likes.get(user_id=current_user.id, post_id=post_id)
    if like is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="like not found")
    await likes.delete(like)
