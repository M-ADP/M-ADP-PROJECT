import pytest

from src.app.dns.exceptions import DNSNameAlreadyExists, DNSNotFound, ProjectAlreadyHasDNS
from src.app.dns.schemas import DNSCreate, DNSPortBinding, DNSUpdate
from src.app.dns.usecase.bind_port_to_dns import BindPortToDNSUseCase
from src.app.dns.usecase.create_dns_for_project import CreateDNSForProjectUseCase
from src.app.dns.usecase.delete_dns_from_project import DeleteDNSFromProjectUseCase
from src.app.dns.usecase.get_dns_for_project import GetDNSForProjectUseCase
from src.app.dns.usecase.update_dns_for_project import UpdateDNSForProjectUseCase
from src.app.port.exceptions import PortNotFound
from src.app.project.exceptions import OnlyOwnerCanManageDNS, ProjectNotFound

from tests.fakes import (
    FakeDNSRepository,
    FakePortRepository,
    FakeProjectMemberRepository,
    FakeProjectRepository,
    FakeProjectResourceClient,
    FakeUnitOfWork,
    make_dns,
    make_member,
    make_port,
    make_project,
)

pytestmark = pytest.mark.anyio


async def test_create_dns_raises_when_project_not_found() -> None:
    usecase = CreateDNSForProjectUseCase(
        uow=FakeUnitOfWork(),
        project_resource_client=FakeProjectResourceClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase("missing", DNSCreate(subdomain="app"), user_id=1)


async def test_create_dns_raises_when_requester_not_owner() -> None:
    project = make_project(1)
    members = [make_member(1, 2, role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = CreateDNSForProjectUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(OnlyOwnerCanManageDNS):
        await usecase(1, DNSCreate(subdomain="app"), user_id=2)


async def test_create_dns_raises_when_project_already_has_dns() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    dns = make_dns(1, 1, dns_name="app.mdeveloper.platform")
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        dns_repo=FakeDNSRepository([dns]),
    )
    usecase = CreateDNSForProjectUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(ProjectAlreadyHasDNS):
        await usecase(1, DNSCreate(subdomain="new"), user_id=1)


async def test_create_dns_raises_when_dns_name_exists() -> None:
    project = make_project(1)
    other_dns = make_dns(2, 2, dns_name="taken.mdeveloper.platform")
    members = [make_member(1, 1, role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        dns_repo=FakeDNSRepository([other_dns]),
    )
    usecase = CreateDNSForProjectUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(DNSNameAlreadyExists):
        await usecase(1, DNSCreate(subdomain="taken"), user_id=1)


async def test_create_dns_success_builds_dns_name_and_calls_client() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    resource_client = FakeProjectResourceClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = CreateDNSForProjectUseCase(uow=uow, project_resource_client=resource_client)

    created = await usecase(1, DNSCreate(subdomain="My-App"), user_id=1)

    assert created.dns_name == "my-app.mdeveloper.platform"
    assert resource_client.calls[0][0] == "create_dns"


async def test_get_dns_raises_when_project_not_found() -> None:
    usecase = GetDNSForProjectUseCase(uow=FakeUnitOfWork())

    with pytest.raises(ProjectNotFound):
        await usecase(project_id="missing", user_id=1)


async def test_get_dns_raises_without_access() -> None:
    project = make_project(1)
    uow = FakeUnitOfWork(project_repo=FakeProjectRepository([project]))
    usecase = GetDNSForProjectUseCase(uow=uow)

    with pytest.raises(ProjectNotFound):
        await usecase(project_id=1, user_id=99)


async def test_get_dns_returns_dns_and_none() -> None:
    project = make_project(1)
    member = make_member(1, 1, role="MEMBER")
    dns = make_dns(1, 1, dns_name="app.mdeveloper.platform")

    uow_with_dns = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository([member]),
        dns_repo=FakeDNSRepository([dns]),
    )
    usecase_with_dns = GetDNSForProjectUseCase(uow=uow_with_dns)

    found = await usecase_with_dns(project_id=1, user_id=1)

    assert found is not None
    assert found.dns_name == "app.mdeveloper.platform"

    uow_without_dns = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository([member]),
        dns_repo=FakeDNSRepository([]),
    )
    usecase_without_dns = GetDNSForProjectUseCase(uow=uow_without_dns)

    not_found = await usecase_without_dns(project_id=1, user_id=1)

    assert not_found is None


async def test_delete_dns_raises_when_project_not_found() -> None:
    usecase = DeleteDNSFromProjectUseCase(
        uow=FakeUnitOfWork(),
        project_resource_client=FakeProjectResourceClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase(project_id="missing", dns_id=1, user_id=1)


async def test_delete_dns_raises_when_requester_not_owner() -> None:
    project = make_project(1)
    members = [make_member(1, 2, role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = DeleteDNSFromProjectUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(OnlyOwnerCanManageDNS):
        await usecase(project_id=1, dns_id=1, user_id=2)


async def test_delete_dns_raises_when_dns_not_found() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = DeleteDNSFromProjectUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(DNSNotFound):
        await usecase(project_id=1, dns_id=1, user_id=1)


async def test_delete_dns_success_calls_resource_client_and_deletes_dns() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    dns = make_dns(1, 1, dns_name="app.mdeveloper.platform")
    resource_client = FakeProjectResourceClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        dns_repo=FakeDNSRepository([dns]),
    )
    usecase = DeleteDNSFromProjectUseCase(uow=uow, project_resource_client=resource_client)

    deleted = await usecase(project_id=1, dns_id=1, user_id=1)

    assert deleted.id == 1
    assert resource_client.calls[0][0] == "delete_dns"
    assert (1, 1) not in uow.dns.dns_records


async def test_update_dns_raises_when_project_not_found() -> None:
    usecase = UpdateDNSForProjectUseCase(
        uow=FakeUnitOfWork(),
        project_resource_client=FakeProjectResourceClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase("missing", 1, DNSUpdate(subdomain="new"), user_id=1)


async def test_update_dns_raises_when_requester_not_owner() -> None:
    project = make_project(1)
    members = [make_member(1, 2, role="MEMBER")]
    dns = make_dns(1, 1, dns_name="old.mdeveloper.platform")
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        dns_repo=FakeDNSRepository([dns]),
    )
    usecase = UpdateDNSForProjectUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(OnlyOwnerCanManageDNS):
        await usecase(1, 1, DNSUpdate(subdomain="new"), user_id=2)


async def test_update_dns_raises_when_dns_not_found() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = UpdateDNSForProjectUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(DNSNotFound):
        await usecase(1, 1, DNSUpdate(subdomain="new"), user_id=1)


async def test_update_dns_raises_when_name_exists() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    current_dns = make_dns(1, 1, dns_name="old.mdeveloper.platform")
    existing_dns = make_dns(2, 2, dns_name="new.mdeveloper.platform")
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        dns_repo=FakeDNSRepository([current_dns, existing_dns]),
    )
    usecase = UpdateDNSForProjectUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(DNSNameAlreadyExists):
        await usecase(1, 1, DNSUpdate(subdomain="new"), user_id=1)


async def test_update_dns_success_updates_name_and_calls_client() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    current_dns = make_dns(1, 1, dns_name="old.mdeveloper.platform")
    resource_client = FakeProjectResourceClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        dns_repo=FakeDNSRepository([current_dns]),
    )
    usecase = UpdateDNSForProjectUseCase(uow=uow, project_resource_client=resource_client)

    updated = await usecase(1, 1, DNSUpdate(subdomain="new-name"), user_id=1)

    assert updated.dns_name == "new-name.mdeveloper.platform"
    assert resource_client.calls[0][0] == "update_dns"


async def test_bind_dns_raises_when_project_not_found() -> None:
    usecase = BindPortToDNSUseCase(
        uow=FakeUnitOfWork(),
        project_resource_client=FakeProjectResourceClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase("missing", 1, DNSPortBinding(port_id=1), user_id=1)


async def test_bind_dns_raises_when_requester_not_owner() -> None:
    project = make_project(1)
    members = [make_member(1, 2, role="MEMBER")]
    dns = make_dns(1, 1, dns_name="app.mdeveloper.platform")
    port = make_port(1, 1)
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        dns_repo=FakeDNSRepository([dns]),
        port_repo=FakePortRepository([port]),
    )
    usecase = BindPortToDNSUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(OnlyOwnerCanManageDNS):
        await usecase(1, 1, DNSPortBinding(port_id=1), user_id=2)


async def test_bind_dns_raises_when_dns_not_found() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    port = make_port(1, 1)
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        port_repo=FakePortRepository([port]),
    )
    usecase = BindPortToDNSUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(DNSNotFound):
        await usecase(1, 1, DNSPortBinding(port_id=1), user_id=1)


async def test_bind_dns_raises_when_port_not_found() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    dns = make_dns(1, 1, dns_name="app.mdeveloper.platform")
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        dns_repo=FakeDNSRepository([dns]),
    )
    usecase = BindPortToDNSUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(PortNotFound):
        await usecase(1, 1, DNSPortBinding(port_id=1), user_id=1)


async def test_bind_dns_success_binds_port_and_calls_resource_client() -> None:
    project = make_project(1)
    members = [make_member(1, 1, role="OWNER")]
    dns = make_dns(1, 1, dns_name="app.mdeveloper.platform")
    port = make_port(1, 1)
    resource_client = FakeProjectResourceClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        dns_repo=FakeDNSRepository([dns]),
        port_repo=FakePortRepository([port]),
    )
    usecase = BindPortToDNSUseCase(uow=uow, project_resource_client=resource_client)

    bound = await usecase(1, 1, DNSPortBinding(port_id=1), user_id=1)

    assert bound.port_id == 1
    assert resource_client.calls[0][0] == "mapping_dns_and_port"
