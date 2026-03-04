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
        self.calls: list[tuple[tuple, dict]] = []

    async def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.result


pytestmark = pytest.mark.anyio


async def test_create_project_port_endpoint_contract() -> None:
    created = make_port(1, 1, from_port=80, port_number=6, protocol="tcp")
    usecase = AsyncUseCaseStub(created)
    payload = PortCreate(from_ip="0.0.0.0/0", from_port=80, port_number=6, protocol="tcp")

    response = await create_project_port_endpoint(
        project_id=1,
        payload=payload,
        user=UserInfo(user_id=1, role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "포트가 공개되었습니다."
    assert response.data.id == 1
    assert response.data.from_port == 80
    assert usecase.calls == [
        ((), {"project_id": 1, "request": payload, "user_id": 1, "role": "OWNER"})
    ]


async def test_list_project_ports_endpoint_contract() -> None:
    page = CursorPage(
        items=[
            PortResponse(
                id=1,
                project_id=1,
                from_ip="0.0.0.0/0",
                from_port=80,
                port_number=6,
                protocol="tcp",
            )
        ],
        has_next=False,
    )
    usecase = AsyncUseCaseStub(page)

    response = await list_project_ports_endpoint(
        project_id=1,
        cursor=0,
        limit=20,
        user=UserInfo(user_id=1, role="MEMBER"),
        usecase=usecase,
    )

    assert response.message == "포트 목록을 조회했습니다."
    assert response.data.items[0].id == 1
    assert usecase.calls == [
        ((), {"project_id": 1, "user_id": 1, "limit": 20, "cursor": 0})
    ]


async def test_update_project_port_endpoint_contract() -> None:
    updated = make_port(1, 1, from_ip="10.0.0.0/24", from_port=8080, port_number=6, protocol="tcp")
    usecase = AsyncUseCaseStub(updated)
    payload = PortUpdate(from_ip="10.0.0.0/24", from_port=8080, port_number=6, protocol="tcp")

    response = await update_project_port_endpoint(
        project_id=1,
        port_id=1,
        payload=payload,
        user=UserInfo(user_id=1, role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "포트가 수정되었습니다."
    assert response.data.from_port == 8080
    assert usecase.calls == [
        ((), {"project_id": 1, "port_id": 1, "request": payload, "user_id": 1, "role": "OWNER"})
    ]


async def test_delete_project_port_endpoint_contract() -> None:
    deleted = make_port(1, 1, from_port=80, port_number=6, protocol="tcp")
    usecase = AsyncUseCaseStub(deleted)

    response = await delete_project_port_endpoint(
        project_id=1,
        port_id=1,
        user=UserInfo(user_id=1, role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "포트가 삭제되었습니다."
    assert response.data.id == 1
    assert usecase.calls == [
        ((), {"project_id": 1, "port_id": 1, "user_id": 1, "role": "OWNER"})
    ]
