import os
import configparser

_config = configparser.ConfigParser()
_config.read("config.ini", encoding="utf-8")


def _get_from_config_or_env(section: str, key: str) -> str:
    result = _config[section].get(key)
    if not result:
        result = os.environ[f"{section}:{key}"]
    return result


DEBUG = int(_get_from_config_or_env("web", "debug"))
SA_ECHO = int(_get_from_config_or_env("web", "sa_echo"))
JWT_ALGORITHM = _get_from_config_or_env("web", "jwt_algorithm")
JWT_SECRET_KEY = _get_from_config_or_env("web", "jwt_secret_key")
ACCESS_TOKEN_EXPIRE_SECONDS = int(_get_from_config_or_env("web", "access_token_expire_seconds"))

SA_URL = _get_from_config_or_env("db", "sa_url")
TEST_SA_URL = _get_from_config_or_env("db", "test_sa_url")
ALEMBIC_SA_URL = _get_from_config_or_env("db", "alembic_sa_url")
