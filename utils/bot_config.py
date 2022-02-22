import os
import configparser

_config = configparser.ConfigParser()
_config.read("config.ini", encoding="utf-8")


def _get_from_config_or_env(section: str, key: str) -> str:
    result = _config[section].get(key)
    if not result:
        result = os.environ[f"{section}:{key}"]
    return result


NUMBER_OF_USERS = int(_get_from_config_or_env("bot", "number_of_users"))
MAX_POSTS_PER_USER = int(_get_from_config_or_env("bot", "max_posts_per_user"))
MAX_LIKES_PER_USER = int(_get_from_config_or_env("bot", "max_likes_per_user"))
BASE_URL = _get_from_config_or_env("bot", "base_url")
