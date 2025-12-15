from fastapi import APIRouter

from api.routers.v1 import ports, projects

v1_api_router = APIRouter(prefix="/v1")
v1_api_router.include_router(projects.router)
v1_api_router.include_router(ports.router)
