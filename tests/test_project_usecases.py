from datetime import datetime, timezone

import pytest

from src.app.project.exceptions import (
    CannotCancelInvitation,
    DiskCannotBeReduced,
    InvitationExpired,
    InvitationNotFound,
    InvitationTargetMismatch,
    MemberInvitationAlreadyExists,
    OnlyOwnerCanAddMembers,
    OnlyOwnerCanDeleteProject,
    OnlyOwnerCanGetResourceLimit,
    OnlyOwnerCanUpdateProjectName,
    OnlyOwnerCanUpdateResource,
    ProjectDeletionFailed,
    ProjectLimitExceeded,
    ProjectNameAlreadyExists,
    ProjectNotFound,
)
from src.app.project.schemas import (
    ProjectCreate,
    ProjectMemberInvite,
    ProjectNameUpdate,
    ProjectResourceUpdate,
)
from src.app.project.usecase.accept_project_member_invitation import (
    AcceptProjectMemberInvitationUseCase,
)
from src.app.project.usecase.cancel_project_member_invitation import (
    CancelProjectMemberInvitationUseCase,
)
from src.app.project.usecase.check_project_available import CheckProjectAvailableUseCase
from src.app.project.usecase.create_project import CreateProjectUseCase
from src.app.project.usecase.delete_project import DeleteProjectUseCase
from src.app.project.usecase.get_project import GetProjectUseCase
from src.app.project.usecase.get_project_resource_limit import GetProjectResourceLimitUseCase
from src.app.project.usecase.invite_project_member import InviteProjectMemberUseCase
from src.app.project.usecase.list_project_member_invitations import (
    ListProjectMemberInvitationsUseCase,
)
from src.app.project.usecase.list_project_members import ListProjectMembersUseCase
from src.app.project.usecase.resend_project_member_invitation import (
    ResendProjectMemberInvitationUseCase,
)
from src.app.project.usecase.list_projects import ListProjectsUseCase
from src.app.project.usecase.update_project_name import UpdateProjectNameUseCase
from src.app.project.usecase.update_project_resource import UpdateProjectResourceUseCase
from src.core.client.application import ApplicationItemData, DeploymentSummaryItem
from src.core.client.project_resource import (
    ProjectResourceSnapshotData,
    ResourceMetricSnapshotData,
    ResourceSnapshotData,
)
from src.core.client.user import UserInfo
from src.core.exceptions import ApplicationServerException, DnsServerException

from tests.fakes import (
    FakeApplicationClient,
    FakeDnsClient,
    FakeProjectInvitationEmailClient,
    FakeProjectInvitationRepository,
    FakeProjectMemberRepository,
    FakeProjectRepository,
    FakeProjectResourceClient,
    FakeUnitOfWork,
    FakeUserClient,
    make_invitation,
    make_member,
    make_project,
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


async def test_create_project_allows_admin_when_project_limit_exceeded() -> None:
    projects = [make_project(i, user_id=1) for i in range(1, 4)]
    uow = FakeUnitOfWork(project_repo=FakeProjectRepository(projects))
    resource_client = FakeProjectResourceClient()
    usecase = CreateProjectUseCase(uow=uow, project_resource_client=resource_client)

    created = await usecase(build_project_create("admin-new"), user_id=1, role="ADMIN")

    assert created.name == "admin-new"
    assert len(uow.project.projects) == 4
    assert resource_client.calls[0][0] == "create"


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
    usecase = DeleteProjectUseCase(
        uow=uow,
        deployment_client=FakeApplicationClient({}),
        dns_client=FakeDnsClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase(project_id="missing", user_id=1, role="OWNER")


async def test_delete_project_raises_when_requester_is_not_owner() -> None:
    project = make_project(1, user_id=1)
    members = [make_member(1, 2, role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = DeleteProjectUseCase(
        uow=uow,
        deployment_client=FakeApplicationClient({}),
        dns_client=FakeDnsClient(),
    )

    with pytest.raises(OnlyOwnerCanDeleteProject):
        await usecase(project_id=1, user_id=2, role="MEMBER")


async def test_delete_project_success() -> None:
    project = make_project(1, user_id=1)
    members = [make_member(1, 1, role="OWNER")]
    deployment_client = FakeApplicationClient({})
    dns_client = FakeDnsClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = DeleteProjectUseCase(
        uow=uow,
        deployment_client=deployment_client,
        dns_client=dns_client,
    )

    deleted = await usecase(project_id=1, user_id=1, role="OWNER")

    assert deleted.id == 1
    assert 1 not in uow.project.projects
    assert deployment_client.delete_requests == [
        {"project_id": 1, "user_id": 1, "role": "OWNER"}
    ]
    assert dns_client.delete_requests == [
        {"project_id": 1, "user_id": 1, "role": "OWNER"}
    ]


async def test_delete_project_raises_when_app_deployment_delete_fails() -> None:
    project = make_project(1, user_id=1)
    members = [make_member(1, 1, role="OWNER")]
    deployment_client = FakeApplicationClient(
        {},
        delete_error=ApplicationServerException("app deployment delete failed"),
    )
    dns_client = FakeDnsClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = DeleteProjectUseCase(
        uow=uow,
        deployment_client=deployment_client,
        dns_client=dns_client,
    )

    with pytest.raises(ProjectDeletionFailed):
        await usecase(project_id=1, user_id=1, role="OWNER")

    assert 1 in uow.project.projects
    assert deployment_client.delete_requests == [
        {"project_id": 1, "user_id": 1, "role": "OWNER"}
    ]
    # deployment_client 에서 에러가 나면 dns_client 는 호출되지 않아야 함 (순서상)
    assert dns_client.delete_requests == []


async def test_delete_project_continues_when_dns_delete_fails() -> None:
    project = make_project(1, user_id=1)
    members = [make_member(1, 1, role="OWNER")]
    deployment_client = FakeApplicationClient({})
    dns_client = FakeDnsClient(
        delete_error=DnsServerException("dns delete failed"),
    )
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = DeleteProjectUseCase(
        uow=uow,
        deployment_client=deployment_client,
        dns_client=dns_client,
    )

    deleted = await usecase(project_id=1, user_id=1, role="OWNER")

    assert deleted.id == 1
    assert 1 not in uow.project.projects
    assert deployment_client.delete_requests == [
        {"project_id": 1, "user_id": 1, "role": "OWNER"}
    ]
    assert dns_client.delete_requests == [
        {"project_id": 1, "user_id": 1, "role": "OWNER"}
    ]


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
    usage = ProjectResourceSnapshotData(
        project_id="1",
        cpu=ResourceMetricSnapshotData(
            limit="1000m",
            used="250m",
            percentage=25,
            unit="m",
        ),
        memory=ResourceMetricSnapshotData(
            limit="1024Mi",
            used="512Mi",
            percentage=50,
            unit="Mi",
        ),
        disk=ResourceMetricSnapshotData(
            limit="10Gi",
            used="2Gi",
            percentage=20,
            unit="Gi",
        ),
        instance=ResourceSnapshotData(
            limit=10,
            used=2,
            percentage=20,
        ),
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
                    health_status="RUNNING",
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
    assert "runtime" not in detail.deployments[0].model_dump()
    assert detail.resource.cpu.percentage == 25
    assert detail.resource.memory.used == "512Mi"
    assert resource_client.calls[0][0] == "get_usage"


async def test_get_project_accepts_upstream_application_status_values() -> None:
    project = make_project(1, name="api-project")
    members = [make_member(1, 1, role="OWNER")]
    resource_client = FakeProjectResourceClient()
    deployment_client = FakeApplicationClient(
        {
            1: [
                ApplicationItemData(
                    id=1,
                    name="web",
                    pod_count=1,
                    health_status="PENDING",
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

    assert detail.deployments[0].health_status == "PENDING"


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


async def test_invite_project_member_creates_pending_invitation_and_sends_email_without_membership() -> None:
    project = make_project(1, user_id=1, name="backend")
    members = [make_member(1, 1, role="OWNER")]
    invitation_repo = FakeProjectInvitationRepository()
    email_client = FakeProjectInvitationEmailClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        project_invitation_repo=invitation_repo,
    )
    usecase = InviteProjectMemberUseCase(
        uow=uow,
        user_client=FakeUserClient(
            [UserInfo(user_id=2, username="Member", email="member@example.com")]
        ),
        email_client=email_client,
    )

    result = await usecase(
        project_id=1,
        request=ProjectMemberInvite(user_id=2),
        user_id=1,
    )

    assert result.project_id == 1
    assert result.invitee_user_id == 2
    assert result.invitee_email == "member@example.com"
    assert result.status == "PENDING"
    assert result.expires_at > result.created_at
    assert (1, 2) not in uow.project_member.members
    saved = next(iter(invitation_repo.invitations.values()))
    assert saved.token_hash
    assert "invite-token" not in saved.token_hash
    sent_url = email_client.sent[0]["invite_url"]
    assert sent_url.startswith(
        "http://localhost:3000/projects/1/member-invitations/"
    )
    assert not sent_url.endswith("/accept")
    assert saved.token_hash not in sent_url
    assert email_client.sent == [
        {
            "to_email": "member@example.com",
            "project_name": "backend",
            "inviter_user_id": 1,
            "invite_url": sent_url,
        }
    ]


async def test_invite_project_member_raises_when_pending_invitation_exists() -> None:
    project = make_project(1, user_id=1)
    members = [make_member(1, 1, role="OWNER")]
    invitation = make_invitation(1, 2)
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
        project_invitation_repo=FakeProjectInvitationRepository([invitation]),
    )
    usecase = InviteProjectMemberUseCase(
        uow=uow,
        user_client=FakeUserClient(
            [UserInfo(user_id=2, username="Member", email="member@example.com")]
        ),
        email_client=FakeProjectInvitationEmailClient(),
    )

    with pytest.raises(MemberInvitationAlreadyExists):
        await usecase(
            project_id=1,
            request=ProjectMemberInvite(user_id=2),
            user_id=1,
        )


async def test_accept_project_member_invitation_adds_member_for_invitee() -> None:
    project = make_project(1, user_id=1)
    invitation = make_invitation(1, 2, token="accept-me")
    invitation_repo = FakeProjectInvitationRepository([invitation])
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_invitation_repo=invitation_repo,
    )
    usecase = AcceptProjectMemberInvitationUseCase(
        uow=uow,
        user_client=FakeUserClient([UserInfo(user_id=2, username="Member")]),
    )

    result = await usecase(project_id=1, token="accept-me", user_id=2)

    assert result.user_id == 2
    assert result.username == "Member"
    assert result.role == "MEMBER"
    assert (1, 2) in uow.project_member.members
    assert invitation_repo.invitations[invitation.id].status == "ACCEPTED"
    assert invitation_repo.invitations[invitation.id].responded_at is not None


async def test_accept_project_member_invitation_rejects_different_user() -> None:
    project = make_project(1, user_id=1)
    invitation = make_invitation(1, 2, token="accept-me")
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_invitation_repo=FakeProjectInvitationRepository([invitation]),
    )
    usecase = AcceptProjectMemberInvitationUseCase(
        uow=uow,
        user_client=FakeUserClient([UserInfo(user_id=99, username="Other")]),
    )

    with pytest.raises(InvitationTargetMismatch):
        await usecase(project_id=1, token="accept-me", user_id=99)

    assert (1, 99) not in uow.project_member.members


async def test_accept_project_member_invitation_raises_when_token_not_found() -> None:
    project = make_project(1, user_id=1)
    usecase = AcceptProjectMemberInvitationUseCase(
        uow=FakeUnitOfWork(project_repo=FakeProjectRepository([project])),
        user_client=FakeUserClient([UserInfo(user_id=2, username="Member")]),
    )

    with pytest.raises(InvitationNotFound):
        await usecase(project_id=1, token="missing", user_id=2)


async def test_accept_project_member_invitation_rejects_expired_invitation() -> None:
    from datetime import timedelta

    project = make_project(1, user_id=1)
    invitation = make_invitation(
        1,
        2,
        token="expired-token",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    invitation_repo = FakeProjectInvitationRepository([invitation])
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_invitation_repo=invitation_repo,
    )
    usecase = AcceptProjectMemberInvitationUseCase(
        uow=uow,
        user_client=FakeUserClient([UserInfo(user_id=2, username="Member")]),
    )

    with pytest.raises(InvitationExpired):
        await usecase(project_id=1, token="expired-token", user_id=2)

    assert (1, 2) not in uow.project_member.members
    assert invitation_repo.invitations[invitation.id].status == "EXPIRED"


async def test_list_project_member_invitations_returns_pending_by_default_for_owner() -> None:
    project = make_project(1, user_id=1)
    invitations = [
        make_invitation(1, 2, invitation_id=10, status="PENDING"),
        make_invitation(1, 3, invitation_id=11, status="ACCEPTED"),
    ]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository([make_member(1, 1, role="OWNER")]),
        project_invitation_repo=FakeProjectInvitationRepository(invitations),
    )
    usecase = ListProjectMemberInvitationsUseCase(uow=uow)

    result = await usecase(project_id=1, user_id=1)

    assert len(result.items) == 1
    assert result.items[0].id == 10
    assert result.items[0].status == "PENDING"
    assert result.has_next is False


async def test_list_project_member_invitations_rejects_non_owner() -> None:
    project = make_project(1, user_id=1)
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository([make_member(1, 2, role="MEMBER")]),
    )
    usecase = ListProjectMemberInvitationsUseCase(uow=uow)

    with pytest.raises(OnlyOwnerCanAddMembers):
        await usecase(project_id=1, user_id=2)


async def test_cancel_project_member_invitation_marks_pending_invitation_canceled() -> None:
    project = make_project(1, user_id=1)
    invitation = make_invitation(1, 2, invitation_id=10, status="PENDING")
    invitation_repo = FakeProjectInvitationRepository([invitation])
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository([make_member(1, 1, role="OWNER")]),
        project_invitation_repo=invitation_repo,
    )
    usecase = CancelProjectMemberInvitationUseCase(uow=uow)

    result = await usecase(project_id=1, invitation_id=10, user_id=1)

    assert result.status == "CANCELED"
    assert invitation_repo.invitations[10].status == "CANCELED"
    assert invitation_repo.invitations[10].responded_at is not None


async def test_cancel_project_member_invitation_rejects_non_pending_invitation() -> None:
    project = make_project(1, user_id=1)
    invitation = make_invitation(1, 2, invitation_id=10, status="ACCEPTED")
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository([make_member(1, 1, role="OWNER")]),
        project_invitation_repo=FakeProjectInvitationRepository([invitation]),
    )
    usecase = CancelProjectMemberInvitationUseCase(uow=uow)

    with pytest.raises(CannotCancelInvitation):
        await usecase(project_id=1, invitation_id=10, user_id=1)


async def test_resend_project_member_invitation_rotates_token_and_sends_email() -> None:
    project = make_project(1, user_id=1, name="backend")
    invitation = make_invitation(1, 2, invitation_id=10, status="PENDING")
    old_hash = invitation.token_hash
    old_expires_at = invitation.expires_at
    invitation_repo = FakeProjectInvitationRepository([invitation])
    email_client = FakeProjectInvitationEmailClient()
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository([make_member(1, 1, role="OWNER")]),
        project_invitation_repo=invitation_repo,
    )
    usecase = ResendProjectMemberInvitationUseCase(uow=uow, email_client=email_client)

    result = await usecase(project_id=1, invitation_id=10, user_id=1)

    assert result.status == "PENDING"
    assert invitation_repo.invitations[10].token_hash != old_hash
    assert result.expires_at > old_expires_at
    assert email_client.sent[0]["to_email"] == "member@example.com"
    assert email_client.sent[0]["project_name"] == "backend"
    assert old_hash not in email_client.sent[0]["invite_url"]
    assert email_client.sent[0]["invite_url"].startswith(
        "http://localhost:3000/projects/1/member-invitations/"
    )
    assert not email_client.sent[0]["invite_url"].endswith("/accept")
