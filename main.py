from fastapi import FastAPI

from src.api.routers import api_router
from src.core.config import get_settings
from src.core import register_exception_handlers
from src.core.middlewares import register_middlewares
from src.core import create_all_tables


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version=settings.app_version)
    register_middlewares(application, settings)
    application.include_router(api_router)
    register_exception_handlers(application)

    @application.on_event("startup")
    async def startup_event() -> None:
        await create_all_tables()

    return application


app = create_app()


@app.get("/")
async def root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
