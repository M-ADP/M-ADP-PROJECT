from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import Settings


def register_middlewares(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_methods=settings.cors.allow_methods,
        allow_credentials=settings.cors.allow_credentials,
        allow_headers=settings.cors.allow_headers,
    )
