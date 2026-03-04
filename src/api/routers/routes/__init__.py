from fastapi import APIRouter

from src.api.routers.routes import dns, ports, projects

routes_api_router = APIRouter()
routes_api_router.include_router(projects.router)
routes_api_router.include_router(ports.router)
routes_api_router.include_router(dns.router)
