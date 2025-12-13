from fastapi import APIRouter

from api.routers.v1 import projects

v1_api_router = APIRouter(prefix="/v1")
v1_api_router.include_router(projects.router)
