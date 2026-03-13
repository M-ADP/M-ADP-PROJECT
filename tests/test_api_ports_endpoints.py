import pytest
from src.api.routers.routes.ports import (
    create_project_port_endpoint,
    delete_project_port_endpoint,
    list_project_ports_endpoint,
    update_project_port_endpoint,
)
from src.app.port.schemas import PortCreate, PortResponse, PortUpdate
from src.common.schemas import CursorPage
from src.dependencies.auth import UserInfo
from tests.fakes import make_port


class AsyncUseCaseStub:
    def __init__(self, result):
        self.result = result
        self.called_with = []

    async def __call__(self, **kwargs):
        self.called_with.append(kwargs)
        return self.result


@pytest.mark.asyncio
async def test_create_project_port_endpoint_contract() -> None:
    created = make_port(1, 1, service_id="svc-1-1")
    usecase = AsyncUseCaseStub(created)
    payload = PortCreate(
        target_deployment_name="app",
        port=80,
        target_port=8080,
        protocol="TCP",
        service_type="ClusterIP",
    )

    response = await create_project_port_endpoint(
        project_id=1,
        payload=payload,
        user=UserInfo(user_id=1, role="OWNER"),
        usecase=usecase,
    )

    assert response.data.service_id == "svc-1-1"
    assert response.data.port == 80
    assert usecase.called_with[0]["request"] == payload


@pytest.mark.asyncio
async def test_list_project_ports_endpoint_contract() -> None:
    page = CursorPage(
        items=[
            PortResponse(
                id=1,
                project_id=1,
                service_id="svc-1-1",
                service_name="svc-1-1",
                target_deployment_name="app",
                port=80,
                target_port=8080,
                protocol="TCP",
                service_type="ClusterIP",
            )
        ],
        has_next=False,
    )
    usecase = AsyncUseCaseStub(page)

    response = await list_project_ports_endpoint(
        project_id=1,
        user=UserInfo(user_id=1, role="MEMBER"),
        usecase=usecase,
    )

    assert len(response.data.items) == 1
    assert response.data.items[0].service_id == "svc-1-1"


@pytest.mark.asyncio
async def test_update_project_port_endpoint_contract() -> None:
    updated = make_port(1, 1, service_id="svc-1-1", port=8080)
    usecase = AsyncUseCaseStub(updated)
    payload = PortUpdate(
        target_deployment_name="app",
        port=8080,
        target_port=8080,
        protocol="TCP",
                        service_type="LoadBalancer",
    )

    response = await update_project_port_endpoint(
        project_id=1,
        port_id=1,
        payload=payload,
        user=UserInfo(user_id=1, role="OWNER"),
        usecase=usecase,
    )

    assert response.data.service_id == "svc-1-1"
    assert response.data.port == 8080


@pytest.mark.asyncio
async def test_delete_project_port_endpoint_contract() -> None:
    deleted = make_port(1, 1)
    usecase = AsyncUseCaseStub(deleted)

    response = await delete_project_port_endpoint(
        project_id=1,
        port_id=1,
        user=UserInfo(user_id=1, role="OWNER"),
        usecase=usecase,
    )

    assert response.data.id == 1
