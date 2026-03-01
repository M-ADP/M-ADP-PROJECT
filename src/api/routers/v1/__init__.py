from fastapi import APIRouter

from src.api.routers.v1 import dns, ports, projects

v1_api_router = APIRouter()
v1_api_router.include_router(projects.router)
v1_api_router.include_router(ports.router)
v1_api_router.include_router(dns.router)
