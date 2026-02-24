from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.middlewares import register_middlewares
from src.api.routers import api_router
from src.common.config.settings import get_settings
from src.core.db import create_all_tables
from src.core.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_all_tables()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    register_middlewares(application, settings)
    application.include_router(api_router)
    register_exception_handlers(application)

    return application
