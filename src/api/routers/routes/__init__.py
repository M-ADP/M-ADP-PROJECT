from fastapi import APIRouter

from src.api.routers.routes import projects, monitoring

routes_api_router = APIRouter()
routes_api_router.include_router(projects.router)
routes_api_router.include_router(monitoring.router)
