import pytest

from src.app.project.exceptions import (
    CannotRemoveOwner,
    CannotTransferOwnershipToSelf,
    MemberAlreadyExists,
    MemberNotFound,
    OnlyOwnerCanAddMembers,
    OnlyOwnerCanRemoveMembers,
    OnlyOwnerCanTransferOwnership,
    OwnershipTransferTargetMustBeMember,
    ProjectNotFound,
    UserNotFound,
)
from src.app.project.schemas import ProjectMemberAdd
from src.app.project.usecase.add_project_member import AddProjectMemberUseCase
from src.app.project.usecase.remove_project_member import RemoveProjectMemberUseCase
from src.app.project.usecase.transfer_project_ownership import TransferProjectOwnershipUseCase
from src.core.client.user import UserInfo

from tests.fakes import (
    FakeProjectMemberRepository,
    FakeProjectRepository,
    FakeUnitOfWork,
    FakeUserClient,
    make_member,
    make_project,
)

pytestmark = pytest.mark.anyio


async def test_add_project_member_raises_when_project_not_found() -> None:
    usecase = AddProjectMemberUseCase(uow=FakeUnitOfWork(), user_client=FakeUserClient())

    with pytest.raises(ProjectNotFound):
        await usecase("missing", ProjectMemberAdd(user_id="target"), user_id="owner")


async def test_add_project_member_raises_when_requester_not_owner() -> None:
    project = make_project("p1")
    members = [make_member("p1", "member", role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = AddProjectMemberUseCase(uow=uow, user_client=FakeUserClient())

    with pytest.raises(OnlyOwnerCanAddMembers):
        await usecase("p1", ProjectMemberAdd(user_id="target"), user_id="member")


async def test_add_project_member_raises_when_member_already_exists() -> None:
    project = make_project("p1")
    members = [
        make_member("p1", "owner", role="OWNER"),
        make_member("p1", "target", role="MEMBER"),
    ]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = AddProjectMemberUseCase(uow=uow, user_client=FakeUserClient())

    with pytest.raises(MemberAlreadyExists):
        await usecase("p1", ProjectMemberAdd(user_id="target"), user_id="owner")


async def test_add_project_member_raises_when_user_not_found() -> None:
    project = make_project("p1")
    members = [make_member("p1", "owner", role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = AddProjectMemberUseCase(uow=uow, user_client=FakeUserClient())

    with pytest.raises(UserNotFound):
        await usecase("p1", ProjectMemberAdd(user_id="target"), user_id="owner")


async def test_add_project_member_success() -> None:
    project = make_project("p1")
    members = [make_member("p1", "owner", role="OWNER")]
    user_client = FakeUserClient(
        [UserInfo(user_id="target", username="Target", profile_image="profile")]
    )
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = AddProjectMemberUseCase(uow=uow, user_client=user_client)

    response = await usecase("p1", ProjectMemberAdd(user_id="target"), user_id="owner")

    assert response.user_id == "target"
    assert response.role == "MEMBER"
    assert response.username == "Target"


async def test_remove_project_member_raises_when_project_not_found() -> None:
    usecase = RemoveProjectMemberUseCase(uow=FakeUnitOfWork(), user_client=FakeUserClient())

    with pytest.raises(ProjectNotFound):
        await usecase("missing", target_user_id="target", user_id="owner")


async def test_remove_project_member_raises_when_requester_not_owner() -> None:
    project = make_project("p1")
    members = [make_member("p1", "member", role="MEMBER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = RemoveProjectMemberUseCase(uow=uow, user_client=FakeUserClient())

    with pytest.raises(OnlyOwnerCanRemoveMembers):
        await usecase("p1", target_user_id="target", user_id="member")


async def test_remove_project_member_raises_when_member_not_found() -> None:
    project = make_project("p1")
    members = [make_member("p1", "owner", role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = RemoveProjectMemberUseCase(uow=uow, user_client=FakeUserClient())

    with pytest.raises(MemberNotFound):
        await usecase("p1", target_user_id="target", user_id="owner")


async def test_remove_project_member_raises_when_target_is_owner() -> None:
    project = make_project("p1")
    members = [
        make_member("p1", "owner", role="OWNER"),
        make_member("p1", "target", role="OWNER"),
    ]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = RemoveProjectMemberUseCase(uow=uow, user_client=FakeUserClient())

    with pytest.raises(CannotRemoveOwner):
        await usecase("p1", target_user_id="target", user_id="owner")


async def test_remove_project_member_success_with_user_info() -> None:
    project = make_project("p1")
    target = make_member("p1", "target", role="MEMBER")
    members = [make_member("p1", "owner", role="OWNER"), target]
    user_client = FakeUserClient(
        [UserInfo(user_id="target", username="Target", profile_image="img")]
    )
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = RemoveProjectMemberUseCase(uow=uow, user_client=user_client)

    response = await usecase("p1", target_user_id="target", user_id="owner")

    assert response.username == "Target"
    assert ("p1", "target") not in uow.project_member.members


async def test_remove_project_member_success_fallback_without_user_info() -> None:
    project = make_project("p1")
    target = make_member("p1", "target", role="MEMBER")
    members = [make_member("p1", "owner", role="OWNER"), target]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = RemoveProjectMemberUseCase(uow=uow, user_client=FakeUserClient())

    response = await usecase("p1", target_user_id="target", user_id="owner")

    assert response.username == "target"
    assert response.profile_image is None


async def test_transfer_ownership_raises_when_project_not_found() -> None:
    usecase = TransferProjectOwnershipUseCase(
        uow=FakeUnitOfWork(),
        user_client=FakeUserClient(),
    )

    with pytest.raises(ProjectNotFound):
        await usecase("missing", target_user_id="target", user_id="owner")


async def test_transfer_ownership_raises_when_target_is_self() -> None:
    project = make_project("p1")
    members = [make_member("p1", "owner", role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = TransferProjectOwnershipUseCase(uow=uow, user_client=FakeUserClient())

    with pytest.raises(CannotTransferOwnershipToSelf):
        await usecase("p1", target_user_id="owner", user_id="owner")


async def test_transfer_ownership_raises_when_requester_not_owner() -> None:
    project = make_project("p1")
    members = [
        make_member("p1", "owner", role="OWNER"),
        make_member("p1", "member", role="MEMBER"),
    ]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = TransferProjectOwnershipUseCase(uow=uow, user_client=FakeUserClient())

    with pytest.raises(OnlyOwnerCanTransferOwnership):
        await usecase("p1", target_user_id="owner", user_id="member")


async def test_transfer_ownership_raises_when_target_member_not_found() -> None:
    project = make_project("p1")
    members = [make_member("p1", "owner", role="OWNER")]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = TransferProjectOwnershipUseCase(uow=uow, user_client=FakeUserClient())

    with pytest.raises(MemberNotFound):
        await usecase("p1", target_user_id="target", user_id="owner")


async def test_transfer_ownership_raises_when_target_not_member_role() -> None:
    project = make_project("p1")
    members = [
        make_member("p1", "owner", role="OWNER"),
        make_member("p1", "target", role="OWNER"),
    ]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = TransferProjectOwnershipUseCase(uow=uow, user_client=FakeUserClient())

    with pytest.raises(OwnershipTransferTargetMustBeMember):
        await usecase("p1", target_user_id="target", user_id="owner")


async def test_transfer_ownership_raises_when_updated_owner_missing() -> None:
    project = make_project("p1")
    owner = make_member("p1", "owner", role="OWNER")
    target = make_member("p1", "target", role="MEMBER")
    repo = FakeProjectMemberRepository([owner, target])
    original_update_role = repo.update_role

    calls = {"count": 0}

    async def flaky_update_role(project_id: str, user_id: str, role: str):
        calls["count"] += 1
        if calls["count"] == 2:
            return None
        return await original_update_role(project_id, user_id, role)

    repo.update_role = flaky_update_role  # type: ignore[method-assign]

    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=repo,
    )
    usecase = TransferProjectOwnershipUseCase(uow=uow, user_client=FakeUserClient())

    with pytest.raises(MemberNotFound):
        await usecase("p1", target_user_id="target", user_id="owner")


async def test_transfer_ownership_success_with_user_info() -> None:
    project = make_project("p1")
    members = [
        make_member("p1", "owner", role="OWNER"),
        make_member("p1", "target", role="MEMBER"),
    ]
    user_client = FakeUserClient(
        [UserInfo(user_id="target", username="Target", profile_image="img")]
    )
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = TransferProjectOwnershipUseCase(uow=uow, user_client=user_client)

    new_owner = await usecase("p1", target_user_id="target", user_id="owner")

    assert new_owner.user_id == "target"
    assert new_owner.role == "OWNER"
    assert uow.project_member.members[("p1", "owner")].role == "MEMBER"


async def test_transfer_ownership_success_fallback_without_user_info() -> None:
    project = make_project("p1")
    members = [
        make_member("p1", "owner", role="OWNER"),
        make_member("p1", "target", role="MEMBER"),
    ]
    uow = FakeUnitOfWork(
        project_repo=FakeProjectRepository([project]),
        project_member_repo=FakeProjectMemberRepository(members),
    )
    usecase = TransferProjectOwnershipUseCase(uow=uow, user_client=FakeUserClient())

    new_owner = await usecase("p1", target_user_id="target", user_id="owner")

    assert new_owner.username == "target"
    assert new_owner.profile_image is None
