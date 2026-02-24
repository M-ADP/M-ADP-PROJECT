import pytest

from src.app.port.exceptions import PortAlreadyExists, PortNotFound
from src.app.port.schemas import PortCreate, PortUpdate
from src.app.port.usecase.create_port import CreatePortUseCase
from src.app.port.usecase.delete_port import DeletePortUseCase
from src.app.port.usecase.list_ports import ListPortsUseCase
from src.app.port.usecase.update_port import UpdatePortUseCase
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

pytestmark = pytest.mark.anyio


def build_port_create(from_port: int = 80) -> PortCreate:
    return PortCreate(from_ip="0.0.0.0/0", from_port=from_port, port_number=6, protocol="tcp")


async def test_create_port_raises_when_project_not_found() -> None:
    usecase = CreatePortUseCase(
        uow=FakeUnitOfWork(),
        project_resource_client=FakeProjectResourceClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase(project_id="missing", request=build_port_create(), user_id="owner")


async def test_create_port_raises_when_requester_not_owner() -> None:
    project = make_project("p1")
    members = [make_member("p1", "member", role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = CreatePortUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(OnlyOwnerCanManagePorts):
        await usecase(project_id="p1", request=build_port_create(), user_id="member")


async def test_create_port_raises_when_port_exists() -> None:
    project = make_project("p1")
    members = [make_member("p1", "owner", role="OWNER")]
    ports = [make_port("p1", "port-1", from_port=80)]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        port_repo=FakePortRepository(ports),
    )
    usecase = CreatePortUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(PortAlreadyExists):
        await usecase(project_id="p1", request=build_port_create(80), user_id="owner")


async def test_create_port_success_calls_resource_client() -> None:
    project = make_project("p1")
    members = [make_member("p1", "owner", role="OWNER")]
    resource_client = FakeProjectResourceClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = CreatePortUseCase(uow=uow, project_resource_client=resource_client)

    created = await usecase(project_id="p1", request=build_port_create(443), user_id="owner")

    assert created.from_port == 443
    assert resource_client.calls[0][0] == "open_port"


async def test_delete_port_raises_when_project_not_found() -> None:
    usecase = DeletePortUseCase(
        uow=FakeUnitOfWork(),
        project_resource_client=FakeProjectResourceClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase(project_id="missing", port_id="port-1", user_id="owner")


async def test_delete_port_raises_when_requester_not_owner() -> None:
    project = make_project("p1")
    members = [make_member("p1", "member", role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = DeletePortUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(OnlyOwnerCanManagePorts):
        await usecase(project_id="p1", port_id="port-1", user_id="member")


async def test_delete_port_raises_when_port_not_found() -> None:
    project = make_project("p1")
    members = [make_member("p1", "owner", role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = DeletePortUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(PortNotFound):
        await usecase(project_id="p1", port_id="port-1", user_id="owner")


async def test_delete_port_success_calls_resource_client_and_deletes_port() -> None:
    project = make_project("p1")
    members = [make_member("p1", "owner", role="OWNER")]
    port = make_port("p1", "port-1", from_port=80)
    resource_client = FakeProjectResourceClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        port_repo=FakePortRepository([port]),
    )
    usecase = DeletePortUseCase(uow=uow, project_resource_client=resource_client)

    deleted = await usecase(project_id="p1", port_id="port-1", user_id="owner")

    assert deleted.id == "port-1"
    assert resource_client.calls[0][0] == "close_port"
    assert ("p1", "port-1") not in uow.port.ports


async def test_list_ports_raises_when_project_not_found() -> None:
    usecase = ListPortsUseCase(uow=FakeUnitOfWork())

    with pytest.raises(ProjectNotFound):
        await usecase(project_id="missing", user_id="user-1", limit=20)


async def test_list_ports_raises_without_access() -> None:
    project = make_project("p1")
    uow = FakeUnitOfWork(project_repo=FakeProjectRepository([project]))
    usecase = ListPortsUseCase(uow=uow)

    with pytest.raises(ProjectNotFound):
        await usecase(project_id="p1", user_id="outsider", limit=20)


async def test_list_ports_success_with_pagination() -> None:
    project = make_project("p1")
    members = [make_member("p1", "user-1")]
    ports = [
        make_port("p1", "port-1", from_port=80),
        make_port("p1", "port-2", from_port=443),
        make_port("p1", "port-3", from_port=53),
    ]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        port_repo=FakePortRepository(ports),
    )
    usecase = ListPortsUseCase(uow=uow)

    result = await usecase(project_id="p1", user_id="user-1", limit=2)

    assert result.has_next is True
    assert [item.id for item in result.items] == ["port-1", "port-2"]


async def test_update_port_raises_when_project_not_found() -> None:
    usecase = UpdatePortUseCase(
        uow=FakeUnitOfWork(),
        project_resource_client=FakeProjectResourceClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase(
            project_id="missing",
            port_id="port-1",
            request=PortUpdate(from_ip="0.0.0.0/0", from_port=8080, port_number=6, protocol="tcp"),
            user_id="owner",
        )


async def test_update_port_raises_when_requester_not_owner() -> None:
    project = make_project("p1")
    members = [make_member("p1", "member", role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = UpdatePortUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(OnlyOwnerCanManagePorts):
        await usecase(
            project_id="p1",
            port_id="port-1",
            request=PortUpdate(from_ip="0.0.0.0/0", from_port=8080, port_number=6, protocol="tcp"),
            user_id="member",
        )


async def test_update_port_raises_when_original_port_not_found() -> None:
    project = make_project("p1")
    members = [make_member("p1", "owner", role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = UpdatePortUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(PortNotFound):
        await usecase(
            project_id="p1",
            port_id="missing-port",
            request=PortUpdate(from_ip="0.0.0.0/0", from_port=8080, port_number=6, protocol="tcp"),
            user_id="owner",
        )


async def test_update_port_raises_when_port_already_exists() -> None:
    project = make_project("p1")
    members = [make_member("p1", "owner", role="OWNER")]
    ports = [
        make_port("p1", "port-1", from_port=80),
        make_port("p1", "port-2", from_port=8080),
    ]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        port_repo=FakePortRepository(ports),
    )
    usecase = UpdatePortUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(PortAlreadyExists):
        await usecase(
            project_id="p1",
            port_id="port-1",
            request=PortUpdate(from_ip="0.0.0.0/0", from_port=8080, port_number=6, protocol="tcp"),
            user_id="owner",
        )


async def test_update_port_success_calls_resource_client() -> None:
    project = make_project("p1")
    members = [make_member("p1", "owner", role="OWNER")]
    original = make_port("p1", "port-1", from_port=80, protocol="tcp")
    resource_client = FakeProjectResourceClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        port_repo=FakePortRepository([original]),
    )
    usecase = UpdatePortUseCase(uow=uow, project_resource_client=resource_client)

    updated = await usecase(
        project_id="p1",
        port_id="port-1",
        request=PortUpdate(from_ip="10.0.0.0/24", from_port=8080, port_number=6, protocol="tcp"),
        user_id="owner",
    )

    assert updated.from_ip == "10.0.0.0/24"
    assert updated.from_port == 8080
    assert resource_client.calls[0][0] == "update_port"
