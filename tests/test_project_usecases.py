import pytest

from src.app.project.exceptions import (
    DiskCannotBeReduced,
    OnlyOwnerCanDeleteProject,
    OnlyOwnerCanGetResourceLimit,
    OnlyOwnerCanUpdateProjectName,
    OnlyOwnerCanUpdateResource,
    ProjectLimitExceeded,
    ProjectNameAlreadyExists,
    ProjectNotFound,
)
from src.app.project.schemas import ProjectCreate, ProjectNameUpdate, ProjectResourceUpdate
from src.app.project.usecase.check_project_available import CheckProjectAvailableUseCase
from src.app.project.usecase.create_project import CreateProjectUseCase
from src.app.project.usecase.delete_project import DeleteProjectUseCase
from src.app.project.usecase.get_project import GetProjectUseCase
from src.app.project.usecase.get_project_resource_limit import GetProjectResourceLimitUseCase
from src.app.project.usecase.list_project_members import ListProjectMembersUseCase
from src.app.project.usecase.list_projects import ListProjectsUseCase
from src.app.project.usecase.update_project_name import UpdateProjectNameUseCase
from src.app.project.usecase.update_project_resource import UpdateProjectResourceUseCase
from src.core.client.application import ApplicationItemData, DeploymentSummaryItem
from src.core.client.project_resource import ResourceUsageData
from src.core.client.user import UserInfo

from tests.fakes import (
    FakeApplicationClient,
    FakeProjectMemberRepository,
    FakeProjectRepository,
    FakeProjectResourceClient,
    FakeUnitOfWork,
    FakeUserClient,
    make_member,
    make_project,
    single_metric,
)

pytestmark = pytest.mark.anyio


def build_project_create(name: str = "my-project") -> ProjectCreate:
    return ProjectCreate(name=name, max_cpu=0.5, max_memory=0.5, max_disk=2.0)


async def test_create_project_raises_when_project_limit_exceeded() -> None:
    projects = [make_project(i, user_id=1) for i in range(1, 4)]
    uow = FakeUnitOfWork(project_repo=FakeProjectRepository(projects))
    resource_client = FakeProjectResourceClient()
    usecase = CreateProjectUseCase(uow=uow, project_resource_client=resource_client)

    with pytest.raises(ProjectLimitExceeded):
        await usecase(build_project_create("new"), user_id=1, role="OWNER")

    assert resource_client.calls == []


async def test_create_project_raises_when_project_name_exists() -> None:
    project = make_project(1, user_id=1, name="duplicate")
    uow = FakeUnitOfWork(project_repo=FakeProjectRepository([project]))
    resource_client = FakeProjectResourceClient()
    usecase = CreateProjectUseCase(uow=uow, project_resource_client=resource_client)

    with pytest.raises(ProjectNameAlreadyExists):
        await usecase(build_project_create("duplicate"), user_id=1, role="OWNER")

    assert len(uow.project.projects) == 1


async def test_create_project_success_creates_owner_member_and_resource() -> None:
    uow = FakeUnitOfWork()
    resource_client = FakeProjectResourceClient()
    usecase = CreateProjectUseCase(uow=uow, project_resource_client=resource_client)

    created = await usecase(build_project_create("backend"), user_id=1, role="OWNER")

    assert created.name == "backend"
    assert uow.project.projects[created.id].name == "backend"
    owner_member = uow.project_member.members[(created.id, 1)]
    assert owner_member.role == "OWNER"
    assert resource_client.calls[0][0] == "create"


async def test_delete_project_raises_when_project_not_found() -> None:
    uow = FakeUnitOfWork()
    usecase = DeleteProjectUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(ProjectNotFound):
        await usecase(project_id="missing", user_id=1, role="OWNER")


async def test_delete_project_raises_when_requester_is_not_owner() -> None:
    project = make_project(1, user_id=1)
    members = [make_member(1, 2, role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = DeleteProjectUseCase(uow=uow, project_resource_client=FakeProjectResourceClient())

    with pytest.raises(OnlyOwnerCanDeleteProject):
        await usecase(project_id=1, user_id=2, role="MEMBER")


async def test_delete_project_success() -> None:
    project = make_project(1, user_id=1)
    members = [make_member(1, 1, role="OWNER")]
    resource_client = FakeProjectResourceClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = DeleteProjectUseCase(uow=uow, project_resource_client=resource_client)

    deleted = await usecase(project_id=1, user_id=1, role="OWNER")

    assert deleted.id == 1
    assert 1 not in uow.project.projects
    assert resource_client.calls[0][0] == "delete"


async def test_update_project_name_raises_when_project_not_found() -> None:
    uow = FakeUnitOfWork()
    usecase = UpdateProjectNameUseCase(uow=uow)

    with pytest.raises(ProjectNotFound):
        await usecase("missing", ProjectNameUpdate(name="new"), user_id=1)


async def test_update_project_name_raises_when_requester_not_owner() -> None:
    project = make_project(1, user_id=1, name="old")
    members = [make_member(1, 2, role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = UpdateProjectNameUseCase(uow=uow)

    with pytest.raises(OnlyOwnerCanUpdateProjectName):
        await usecase(1, ProjectNameUpdate(name="new"), user_id=2)


async def test_update_project_name_raises_when_name_exists() -> None:
    projects = [
        make_project(1, user_id=1, name="old"),
        make_project(2, user_id=1, name="new"),
    ]
    members = [make_member(1, 1, role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository(projects),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = UpdateProjectNameUseCase(uow=uow)

    with pytest.raises(ProjectNameAlreadyExists):
        await usecase(1, ProjectNameUpdate(name="new"), user_id=1)


async def test_update_project_name_success() -> None:
    project = make_project(1, user_id=1, name="old")
    members = [make_member(1, 1, role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = UpdateProjectNameUseCase(uow=uow)

    updated = await usecase(1, ProjectNameUpdate(name="new"), user_id=1)

    assert updated.name == "new"


async def test_update_project_resource_raises_when_project_not_found() -> None:
    usecase = UpdateProjectResourceUseCase(
        uow=FakeUnitOfWork(),
        project_resource_client=FakeProjectResourceClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase(
            project_id="missing",
            request=ProjectResourceUpdate(max_cpu=1.0),
            user_id=1,
            role="OWNER",
        )


async def test_update_project_resource_raises_when_requester_not_owner() -> None:
    project = make_project(1, user_id=1, max_disk=2.0)
    members = [make_member(1, 2, role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = UpdateProjectResourceUseCase(
        uow=uow,
        project_resource_client=FakeProjectResourceClient(),
    )

    with pytest.raises(OnlyOwnerCanUpdateResource):
        await usecase(
            project_id=1,
            request=ProjectResourceUpdate(max_disk=3.0),
            user_id=2,
            role="MEMBER",
        )


async def test_update_project_resource_raises_when_disk_is_reduced() -> None:
    project = make_project(1, user_id=1, max_disk=3.0)
    members = [make_member(1, 1, role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = UpdateProjectResourceUseCase(
        uow=uow,
        project_resource_client=FakeProjectResourceClient(),
    )

    with pytest.raises(DiskCannotBeReduced):
        await usecase(
            project_id=1,
            request=ProjectResourceUpdate(max_disk=2.5),
            user_id=1,
            role="OWNER",
        )


async def test_update_project_resource_success_allocates_resource() -> None:
    project = make_project(1, user_id=1, max_cpu=1.0, max_memory=0.5, max_disk=2.0)
    members = [make_member(1, 1, role="OWNER")]
    resource_client = FakeProjectResourceClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = UpdateProjectResourceUseCase(
        uow=uow,
        project_resource_client=resource_client,
    )

    updated = await usecase(
        project_id=1,
        request=ProjectResourceUpdate(max_cpu=2.0, max_memory=1.0, max_disk=3.0),
        user_id=1,
        role="OWNER",
    )

    assert updated.max_cpu == 2.0
    assert updated.max_memory == 1.0
    assert updated.max_disk == 3.0
    assert resource_client.calls[-1][0] == "allocate"


async def test_get_project_raises_when_project_not_found() -> None:
    usecase = GetProjectUseCase(
        uow=FakeUnitOfWork(),
        project_resource_client=FakeProjectResourceClient(),
        deployment_client=FakeApplicationClient({}),
    )

    with pytest.raises(ProjectNotFound):
        await usecase(project_id="missing", user_id=1, role="OWNER")


async def test_get_project_raises_when_user_has_no_role() -> None:
    project = make_project(1)
    uow = FakeUnitOfWork(project_repo=FakeProjectRepository([project]))
    usecase = GetProjectUseCase(
        uow=uow,
        project_resource_client=FakeProjectResourceClient(),
        deployment_client=FakeApplicationClient({}),
    )

    with pytest.raises(ProjectNotFound):
        await usecase(project_id=1, user_id=99, role="USER")


async def test_get_project_success_maps_all_fields() -> None:
    project = make_project(1, name="api-project")
    members = [make_member(1, 1, role="OWNER")]
    usage = ResourceUsageData(
        cpu=single_metric(0.1),
        memory=single_metric(10.0),
        disk=single_metric(20.0),
        network=single_metric(30.0),
        traffic_per_hour=single_metric(40.0),
    )
    resource_client = FakeProjectResourceClient(usage=usage)
    deployment_client = FakeApplicationClient(
        {
            1: [
                ApplicationItemData(
                    id=1,
                    name="web",
                    runtime="python",
                    pod_count=2,
                    exposed_port=80,
                    cpu_usage_percent=12.5,
                    ram_usage_percent=45.0,
                    health_status="Healthy",
                )
            ]
        }
    )
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = GetProjectUseCase(
        uow=uow,
        project_resource_client=resource_client,
        deployment_client=deployment_client,
    )

    detail = await usecase(project_id=1, user_id=1, role="OWNER")

    assert detail.id == 1
    assert detail.name == "api-project"
    assert detail.my_role == "OWNER"
    assert detail.deployments[0].name == "web"
    assert detail.cpu_usage[0].value == 0.1
    assert resource_client.calls[0][0] == "get_usage"


async def test_list_projects_applies_order_default_role_and_state_fallback() -> None:
    projects = [
        make_project(10, name="A"),
        make_project(20, name="B"),
        make_project(30, name="C"),
        make_project(40, name="D"),
    ]
    members = [
        make_member(10, 1, role="OWNER"),
        make_member(20, 1, role="MEMBER"),
    ]
    project_member_repo = FakeProjectMemberRepository(
        members,
        project_ids_override={1: [10, 20, 30, 40]},
    )
    summary_client = FakeApplicationClient(
        summaries=[
            DeploymentSummaryItem(
                project_id=20,
                running=3,
                warning=1,
                state="BROKEN",
            )
        ]
    )
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository(projects, reverse_get_by_ids=True),
        project_member_repo=project_member_repo,
    )
    usecase = ListProjectsUseCase(uow=uow, application_client=summary_client)

    result = await usecase(user_id=1, role="USER", limit=3)

    assert result.has_next is True
    assert [item.id for item in result.items] == [10, 20, 30]
    assert result.items[1].deployment_status.state == "FAILED"
    assert result.items[2].my_role == "MEMBER"


async def test_list_projects_empty_ids_skips_summary_lookup() -> None:
    project_member_repo = FakeProjectMemberRepository(project_ids_override={1: []})
    summary_client = FakeApplicationClient()
    uow = FakeUnitOfWork(project_member_repo=project_member_repo)
    usecase = ListProjectsUseCase(uow=uow, application_client=summary_client)

    result = await usecase(user_id=1, role="USER", limit=20)

    assert result.items == []
    assert result.has_next is False
    assert summary_client.requests == []


@pytest.mark.parametrize(
    "members, expected",
    [
        ([make_member(1, 1)], True),
        ([], False),
    ],
)
async def test_check_project_available_returns_member_access(
    members: list,
    expected: bool,
) -> None:
    uow = FakeUnitOfWork(project_member_repo=FakeProjectMemberRepository(members))
    usecase = CheckProjectAvailableUseCase(uow=uow)

    result = await usecase(project_id=1, user_id=1)

    assert result is expected


async def test_get_project_resource_limit_raises_when_project_not_found() -> None:
    usecase = GetProjectResourceLimitUseCase(uow=FakeUnitOfWork())

    with pytest.raises(ProjectNotFound):
        await usecase(project_id=999, user_id=1)


async def test_get_project_resource_limit_raises_when_requester_not_owner() -> None:
    project = make_project(1)
    members = [make_member(1, 2, role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = GetProjectResourceLimitUseCase(uow=uow)

    with pytest.raises(OnlyOwnerCanGetResourceLimit):
        await usecase(project_id=1, user_id=2)


async def test_get_project_resource_limit_returns_project_limits() -> None:
    project = make_project(1, max_cpu=2.0, max_memory=1024.0, max_disk=2048.0)
    members = [make_member(1, 1, role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = GetProjectResourceLimitUseCase(uow=uow)

    result = await usecase(project_id=1, user_id=1)

    assert result.project_id == 1
    assert result.max_cpu == 2.0
    assert result.max_memory == 1024.0
    assert result.max_disk == 2048.0


async def test_list_project_members_raises_when_project_not_found() -> None:
    usecase = ListProjectMembersUseCase(
        uow=FakeUnitOfWork(),
        user_client=FakeUserClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase(project_id="missing", user_id=1)


async def test_list_project_members_raises_without_access() -> None:
    project = make_project(1)
    uow = FakeUnitOfWork(project_repo=FakeProjectRepository([project]))
    usecase = ListProjectMembersUseCase(uow=uow, user_client=FakeUserClient())

    with pytest.raises(ProjectNotFound):
        await usecase(project_id=1, user_id=1)


async def test_list_project_members_success_with_pagination_and_fallback_user_info() -> None:
    project = make_project(1)
    members = [
        make_member(1, 1, member_id=1, role="OWNER"),
        make_member(1, 2, member_id=2, role="MEMBER"),
        make_member(1, 3, member_id=3, role="MEMBER"),
    ]
    user_client = FakeUserClient([
        UserInfo(user_id=1, username="Owner", profile_image="img"),
        UserInfo(user_id=2, username="Member1", profile_image=None),
    ])
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = ListProjectMembersUseCase(uow=uow, user_client=user_client)

    result = await usecase(project_id=1, user_id=1, limit=2)

    assert result.has_next is True
    assert len(result.items) == 2
    assert result.items[0].username == "Owner"
    assert result.items[1].username == "Member1"
    assert result.items[1].profile_image is None
