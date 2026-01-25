from fastapi import APIRouter

from src.api.routers import health
from src.api.routers.v1 import v1_api_router

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(v1_api_router)
