import pytest
from src.app.port.exceptions import PortAlreadyExists, PortNotFound
from src.app.port.schemas import PortCreate, PortUpdate
from src.app.port.usecase import (
    CreatePortUseCase,
    DeletePortUseCase,
    ListPortsUseCase,
    UpdatePortUseCase,
)
from src.app.project.exceptions import OnlyOwnerCanManagePorts, ProjectNotFound
from tests.fakes import (
    FakePortRepository,
    FakeProjectMemberRepository,
    FakeProjectRepository,
    FakeProjectResourceClient,
    FakeUnitOfWork,
    make_member,
    make_port,
    make_project,
)


def build_port_create() -> PortCreate:
    return PortCreate(
        target_deployment_name="app",
        port=80,
        target_port=8080,
        protocol="TCP",
        service_type="LoadBalancer",
    )


def build_port_update() -> PortUpdate:
    return PortUpdate(
        target_deployment_name="app-updated",
        port=443,
        target_port=8443,
        protocol="TCP",
        service_type="ClusterIP",
    )


@pytest.mark.asyncio
async def test_create_port_raises_when_project_not_found() -> None:
    usecase = CreatePortUseCase(
        uow=FakeUnitOfWork(),
        project_resource_client=FakeProjectResourceClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase(
            project_id=1,
            request=build_port_create(),
            user_id=1,
            role="OWNER",
        )


@pytest.mark.asyncio
async def test_create_port_raises_when_requester_not_owner() -> None:
    project = make_project(1)
    members = [make_member(1, 2, role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = CreatePortUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(OnlyOwnerCanManagePorts):
        await usecase(
            project_id=1,
            request=build_port_create(),
            user_id=2,
            role="MEMBER",
        )


@pytest.mark.asyncio
async def test_create_port_success_calls_resource_client_and_returns_port() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    resource_client = FakeProjectResourceClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = CreatePortUseCase(uow=uow, project_resource_client=resource_client)

    request = build_port_create()
    port = await usecase(
        project_id=1,
        request=request,
        user_id=1,
        role="OWNER",
    )

    assert port.project_id == 1
    assert port.service_id.startswith("svc-1-")
    assert port.port == request.port
    assert any(call[0] == "open_port" for call in resource_client.calls)


@pytest.mark.asyncio
async def test_list_ports_returns_ports_for_project() -> None:
    project = make_project(1)
    member = make_member(1, 1, role="MEMBER")
    ports = [
        make_port(1, 1, service_id="svc-1"),
        make_port(1, 2, service_id="svc-2"),
        make_port(2, 3, service_id="svc-3"),
    ]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository([member]),
        port_repo=FakePortRepository(ports),
    )
    usecase = ListPortsUseCase(uow=uow)

    result = await usecase(project_id=1, user_id=1, limit=10)

    assert len(result.items) == 2
    assert result.items[0].service_id == "svc-1"
    assert result.items[1].service_id == "svc-2"


@pytest.mark.asyncio
async def test_delete_port_raises_when_port_not_found() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = DeletePortUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(PortNotFound):
        await usecase(project_id=1, port_id=999, user_id=1, role="OWNER")


@pytest.mark.asyncio
async def test_delete_port_success_calls_resource_client_and_deletes_port() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    port = make_port(1, 1, service_id="web-svc")
    resource_client = FakeProjectResourceClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        port_repo=FakePortRepository([port]),
    )
    usecase = DeletePortUseCase(uow=uow, project_resource_client=resource_client)

    await usecase(project_id=1, port_id=1, user_id=1, role="OWNER")

    assert any(call[0] == "close_port" for call in resource_client.calls)
    assert await uow.port.get_by_id_for_project(1, 1) is None


@pytest.mark.asyncio
async def test_update_port_raises_when_project_not_found() -> None:
    usecase = UpdatePortUseCase(
        uow=FakeUnitOfWork(),
        project_resource_client=FakeProjectResourceClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase(
            project_id=1,
            port_id=1,
            request=build_port_update(),
            user_id=1,
            role="OWNER",
        )


@pytest.mark.asyncio
async def test_update_port_raises_when_requester_not_owner() -> None:
    project = make_project(1)
    members = [make_member(1, 2, role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = UpdatePortUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(OnlyOwnerCanManagePorts):
        await usecase(
            project_id=1,
            port_id=1,
            request=build_port_update(),
            user_id=2,
            role="MEMBER",
        )


@pytest.mark.asyncio
async def test_update_port_raises_when_original_port_not_found() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = UpdatePortUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(PortNotFound):
        await usecase(
            project_id=1,
            port_id=999,
            request=build_port_update(),
            user_id=1,
            role="OWNER",
        )


@pytest.mark.asyncio
async def test_update_port_success_calls_resource_client() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    original = make_port(1, 1, service_id="web-svc")
    resource_client = FakeProjectResourceClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        port_repo=FakePortRepository([original]),
    )
    usecase = UpdatePortUseCase(uow=uow, project_resource_client=resource_client)

    request = build_port_update()
    updated = await usecase(
        project_id=1,
        port_id=1,
        request=request,
        user_id=1,
        role="OWNER",
    )

    assert updated.port == request.port
    assert updated.service_id == original.service_id
    assert any(call[0] == "update_port" for call in resource_client.calls)
