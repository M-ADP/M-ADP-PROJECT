from fastapi import FastAPI

from src.api.routers import api_router
from src.common.config.settings import get_app_config, load_all_configs
from src.core.db import create_all_tables
from src.core.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    app_config = get_app_config()
    application = FastAPI(title=app_config.app_name, version=app_config.app_version)
    application.include_router(api_router)
    register_exception_handlers(application)

    @application.on_event("startup")
    async def startup_event() -> None:
        load_all_configs()
        await create_all_tables()

    return application
