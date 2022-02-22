import asyncio
import logging
import random
import argparse

import requests
from sqlalchemy import select, delete

from db.sa_models import UserModel, PostModel, LikeModel
from utils import bot_config as cfg
from db.core import DBSession


logging.basicConfig(level=logging.INFO)


def main():
    posts_ids = []

    for user_num in range(cfg.NUMBER_OF_USERS):
        user = requests.post(cfg.BASE_URL + "/sign_up", data={"username": f"bot-user{user_num}", "password": f"pwd"})
        logging.info(f"user created: {user.json()}")
        token = requests.post(cfg.BASE_URL + "/token", data={"username": f"bot-user{user_num}", "password": f"pwd"})
        token = token.json()["access_token"]
        for _ in range(random.randint(1, cfg.MAX_POSTS_PER_USER)):
            post = requests.post(cfg.BASE_URL + "/posts?fields=user", json={}, headers={"Authorization": f"Bearer {token}"})
            posts_ids.append(post.json()["id"])
            logging.info(f"post created: {post.json()}")

    for user_num in range(cfg.NUMBER_OF_USERS):
        token = requests.post(cfg.BASE_URL + "/token", data={"username": f"bot-user{user_num}", "password": f"pwd"})
        token = token.json()["access_token"]

        for _ in range(random.randint(1, cfg.MAX_LIKES_PER_USER)):
            post_id = random.choice(posts_ids)
            like_result = requests.post(cfg.BASE_URL + f"/posts/{post_id}/like",
                                        headers={"Authorization": f"Bearer {token}"})
            if like_result.status_code == 200:
                logging.info(f"post liked: {post_id} (user: bot-user{user_num})")
            else:
                logging.info(f"post not liked: {post_id} (user: bot-user{user_num})"
                             f"details:({like_result.status_code}) {like_result.json()}")


async def clear():
    async with DBSession() as s:
        async with s.begin():
            bot_users = select(UserModel).filter(UserModel.username.startswith("bot-user"))
            bot_users = await s.scalars(bot_users)
            bot_user_ids = [bot_user.id for bot_user in bot_users]
            await s.execute(delete(PostModel).filter(PostModel.user_id.in_(bot_user_ids)))
            await s.execute(delete(LikeModel).filter(LikeModel.user_id.in_(bot_user_ids)))
            await s.execute(delete(UserModel).filter(UserModel.id.in_(bot_user_ids)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="create random users, posts, likes")
    parser.add_argument(
        "-c", "--clear",
        action="store_true",
        help="clear all users with username starting with 'bot-user', "
             "all posts/likes created by them; doesn't create anything, only deletes"
    )
    args = parser.parse_args()
    if args.clear is True:
        logging.info("Clearing started!")
        asyncio.run(clear())
        logging.info("Clearing finished!")
    else:
        logging.info("Random users/posts/likes creation started!")
        main()
        logging.info("Random users/posts/likes creation finished!")
