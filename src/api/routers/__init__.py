from fastapi import APIRouter

from src.api.routers import health
from src.api.routers.routes import routes_api_router

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(routes_api_router)
