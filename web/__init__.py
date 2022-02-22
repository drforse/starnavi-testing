from fastapi import FastAPI

from utils import config
from .routers import routers


def app():
    app_ = FastAPI(debug=config.DEBUG)

    for router in routers:
        app_.include_router(router)
    return app_
