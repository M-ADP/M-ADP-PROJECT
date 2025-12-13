from fastapi import FastAPI

from api.routers import api_router
from core.config import get_settings
from core.exceptions import register_exception_handlers
from core.middlewares import register_middlewares


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version=settings.app_version)
    register_middlewares(application, settings)
    application.include_router(api_router)
    register_exception_handlers(application)
    return application


app = create_app()


@app.get("/")
async def root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
