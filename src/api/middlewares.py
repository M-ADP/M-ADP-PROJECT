from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.common.config.settings import AppConfig


def register_middlewares(app: FastAPI, app_config: AppConfig) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.cors.allow_origins,
        allow_methods=app_config.cors.allow_methods,
        allow_credentials=app_config.cors.allow_credentials,
        allow_headers=app_config.cors.allow_headers,
    )
