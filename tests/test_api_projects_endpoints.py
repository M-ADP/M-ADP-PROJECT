from datetime import datetime, timezone

import pytest

from src.api.routers.v1.projects import (
    add_project_member_endpoint,
    create_project_endpoint,
    delete_project_endpoint,
    get_project_endpoint,
    list_project_members_endpoint,
    list_projects_endpoint,
    remove_project_member_endpoint,
    transfer_project_ownership_endpoint,
    update_project_name_endpoint,
    update_project_resource_endpoint,
)
from src.app.port.schemas import PortResponse
from src.app.project.schemas import (
    DeploymentItem,
    MetricPoint,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectListItemResponse,
    ProjectMemberAdd,
    ProjectMemberResponse,
    ProjectNameUpdate,
    ProjectOwnerTransfer,
    ProjectResourceUpdate,
)
from src.common.schemas import CursorPage
from src.dependencies.auth import UserInfo

from tests.fakes import make_project


class AsyncUseCaseStub:
    def __init__(self, result):
        self.result = result
        self.calls: list[tuple[tuple, dict]] = []

    async def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.result


pytestmark = pytest.mark.anyio


async def test_create_project_endpoint_contract() -> None:
    created = make_project(1, user_id="u1", name="alpha", max_cpu=1.0, max_memory=128.0, max_disk=256.0)
    usecase = AsyncUseCaseStub(created)

    response = await create_project_endpoint(
        payload=ProjectCreate(name="alpha", max_cpu=1.0, max_memory=128.0, max_disk=256.0),
        user=UserInfo(user_id="u1", role="MEMBER"),
        usecase=usecase,
    )

    assert response.message == "프로젝트가 생성되었습니다."
    assert response.data.id == 1
    assert response.data.name == "alpha"
    assert usecase.calls == [((ProjectCreate(name="alpha", max_cpu=1.0, max_memory=128.0, max_disk=256.0),), {"user_id": "u1"})]


async def test_list_projects_endpoint_contract() -> None:
    page = CursorPage(
        items=[
            ProjectListItemResponse.model_validate(
                {
                    "id": 1,
                    "name": "alpha",
                    "my_role": "OWNER",
                    "domain": "alpha.mdeveloper.platform",
                    "deployment_summary": {"running": 1, "warning": 0},
                    "deployment_status": {"state": "RUNNING", "message": "ok"},
                }
            )
        ],
        has_next=False,
    )
    usecase = AsyncUseCaseStub(page)

    response = await list_projects_endpoint(
        cursor=0,
        limit=10,
        user=UserInfo(user_id="u1", role="MEMBER"),
        usecase=usecase,
    )

    assert response.message == "프로젝트 목록을 조회했습니다."
    assert response.data.items[0].id == 1
    assert response.data.items[0].deployment_status.state == "RUNNING"
    assert usecase.calls == [
        ((), {"user_id": "u1", "limit": 10, "cursor": 0})
    ]


async def test_get_project_endpoint_contract() -> None:
    detail = ProjectDetailResponse(
        id=1,
        name="alpha",
        my_role="OWNER",
        deployments=[DeploymentItem(id="d1", name="web", runtime="python", pod_count=1, health_status="Healthy")],
        cpu_usage=[MetricPoint(timestamp="2026-01-01T00:00:00Z", value=0.1)],
        memory_usage=[MetricPoint(timestamp="2026-01-01T00:00:00Z", value=10.0)],
        disk_usage=[MetricPoint(timestamp="2026-01-01T00:00:00Z", value=20.0)],
        network_usage=[MetricPoint(timestamp="2026-01-01T00:00:00Z", value=30.0)],
        traffic_per_hour=[MetricPoint(timestamp="2026-01-01T00:00:00Z", value=40.0)],
        ports=[
            PortResponse(
                id=1,
                project_id=1,
                from_ip="0.0.0.0/0",
                from_port=80,
                port_number=6,
                protocol="tcp",
            )
        ],
    )
    usecase = AsyncUseCaseStub(detail)

    response = await get_project_endpoint(
        project_id=1,
        user=UserInfo(user_id="u1", role="MEMBER"),
        usecase=usecase,
    )

    assert response.message == "프로젝트를 조회했습니다."
    assert response.data.id == 1
    assert response.data.deployments[0].id == "d1"
    assert usecase.calls == [((1,), {"user_id": "u1"})]


async def test_update_project_name_endpoint_contract() -> None:
    updated = make_project(1, user_id="u1", name="beta")
    usecase = AsyncUseCaseStub(updated)
    payload = ProjectNameUpdate(name="beta")

    response = await update_project_name_endpoint(
        project_id=1,
        payload=payload,
        user=UserInfo(user_id="u1", role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "프로젝트 이름이 변경되었습니다."
    assert response.data.name == "beta"
    assert usecase.calls == [((1, payload), {"user_id": "u1"})]


async def test_delete_project_endpoint_contract() -> None:
    deleted = make_project(1, user_id="u1", name="alpha")
    usecase = AsyncUseCaseStub(deleted)

    response = await delete_project_endpoint(
        project_id=1,
        user=UserInfo(user_id="u1", role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "프로젝트가 삭제되었습니다."
    assert response.data.id == 1
    assert usecase.calls == [((1,), {"user_id": "u1"})]


async def test_update_project_resource_endpoint_contract() -> None:
    updated = make_project(1, user_id="u1", name="alpha", max_cpu=2.0, max_memory=256.0, max_disk=512.0)
    usecase = AsyncUseCaseStub(updated)
    payload = ProjectResourceUpdate(max_cpu=2.0, max_memory=256.0, max_disk=512.0)

    response = await update_project_resource_endpoint(
        project_id=1,
        payload=payload,
        user=UserInfo(user_id="u1", role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "프로젝트 리소스가 변경되었습니다."
    assert response.data.max_cpu == 2.0
    assert response.data.max_memory == 256.0
    assert response.data.max_disk == 512.0
    assert usecase.calls == [
        ((1,), {"request": payload, "user_id": "u1"})
    ]


async def test_list_project_members_endpoint_contract() -> None:
    joined = datetime(2026, 1, 1, tzinfo=timezone.utc)
    page = CursorPage(
        items=[
            ProjectMemberResponse(
                user_id="u1",
                username="owner",
                profile_image=None,
                role="OWNER",
                joined_at=joined,
            )
        ],
        has_next=False,
    )
    usecase = AsyncUseCaseStub(page)

    response = await list_project_members_endpoint(
        project_id=1,
        cursor="m0",
        limit=20,
        user=UserInfo(user_id="u1", role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "멤버 목록을 조회했습니다."
    assert response.data.items[0].user_id == "u1"
    assert usecase.calls == [
        ((), {"project_id": 1, "user_id": "u1", "limit": 20, "cursor": "m0"})
    ]


async def test_add_project_member_endpoint_contract() -> None:
    joined = datetime(2026, 1, 1, tzinfo=timezone.utc)
    member = ProjectMemberResponse(
        user_id="u2",
        username="member",
        profile_image="img",
        role="MEMBER",
        joined_at=joined,
    )
    usecase = AsyncUseCaseStub(member)
    payload = ProjectMemberAdd(user_id="u2")

    response = await add_project_member_endpoint(
        project_id=1,
        payload=payload,
        user=UserInfo(user_id="u1", role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "멤버가 추가되었습니다."
    assert response.data.user_id == "u2"
    assert usecase.calls == [
        ((), {"project_id": 1, "request": payload, "user_id": "u1"})
    ]


async def test_remove_project_member_endpoint_contract() -> None:
    joined = datetime(2026, 1, 1, tzinfo=timezone.utc)
    member = ProjectMemberResponse(
        user_id="u2",
        username="member",
        profile_image=None,
        role="MEMBER",
        joined_at=joined,
    )
    usecase = AsyncUseCaseStub(member)

    response = await remove_project_member_endpoint(
        project_id=1,
        target_user_id="u2",
        user=UserInfo(user_id="u1", role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "멤버가 제거되었습니다."
    assert response.data.user_id == "u2"
    assert usecase.calls == [
        ((), {"project_id": 1, "target_user_id": "u2", "user_id": "u1"})
    ]


async def test_transfer_project_ownership_endpoint_contract() -> None:
    joined = datetime(2026, 1, 1, tzinfo=timezone.utc)
    new_owner = ProjectMemberResponse(
        user_id="u2",
        username="new-owner",
        profile_image=None,
        role="OWNER",
        joined_at=joined,
    )
    usecase = AsyncUseCaseStub(new_owner)
    payload = ProjectOwnerTransfer(target_user_id="u2")

    response = await transfer_project_ownership_endpoint(
        project_id=1,
        payload=payload,
        user=UserInfo(user_id="u1", role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "프로젝트 소유자가 변경되었습니다."
    assert response.data.role == "OWNER"
    assert usecase.calls == [
        ((), {"project_id": 1, "target_user_id": "u2", "user_id": "u1"})
    ]
