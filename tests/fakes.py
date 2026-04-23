from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from src.core.client.application import ApplicationItemData, DeploymentSummaryItem
from src.core.client.project_resource import (
    ProjectResourceSnapshotData,
    ResourceMetricSnapshotData,
    ResourceSnapshotData,
)
from src.core.client.user import UserInfo
from src.app.project.invitation_security import hash_invitation_token
from src.core.domain.project import Project, ProjectInvitation, ProjectMember


def make_project(
    project_id: int,
    *,
    user_id: int = 1,
    name: str | None = None,
    max_cpu: float = 1.0,
    max_memory: float = 128.0,
    max_disk: float = 256.0,
) -> Project:
    return Project(
        id=project_id,
        user_id=user_id,
        name=name or f"project-{project_id}",
        max_cpu=max_cpu,
        max_memory=max_memory,
        max_disk=max_disk,
    )


def make_member(
    project_id: int,
    user_id: int,
    *,
    member_id: int | None = None,
    role: str = "MEMBER",
    joined_at: datetime | None = None,
) -> ProjectMember:
    return ProjectMember(
        id=member_id or abs(hash(f"m-{project_id}-{user_id}")),
        project_id=project_id,
        user_id=user_id,
        role=role,
        joined_at=joined_at or datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


def make_invitation(
    project_id: int,
    invitee_user_id: int,
    *,
    invitation_id: int | None = None,
    inviter_user_id: int = 1,
    invitee_email: str = "member@example.com",
    token: str = "invite-token",
    token_hash: str | None = None,
    status: str = "PENDING",
    created_at: datetime | None = None,
    expires_at: datetime | None = None,
    responded_at: datetime | None = None,
) -> ProjectInvitation:
    created = created_at or datetime.now(timezone.utc)
    return ProjectInvitation(
        id=invitation_id or abs(hash(f"i-{project_id}-{invitee_user_id}")),
        project_id=project_id,
        inviter_user_id=inviter_user_id,
        invitee_user_id=invitee_user_id,
        invitee_email=invitee_email,
        token_hash=token_hash or hash_invitation_token(token),
        status=status,
        created_at=created,
        expires_at=expires_at or created + timedelta(days=7),
        responded_at=responded_at,
    )


class FakeProjectRepository:
    def __init__(
        self,
        projects: list[Project] | None = None,
        *,
        reverse_get_by_ids: bool = False,
    ) -> None:
        self.projects: dict[int, Project] = {
            project.id: project for project in (projects or [])
        }
        self.reverse_get_by_ids = reverse_get_by_ids

    async def count_by_user(self, user_id: int) -> int:
        return sum(1 for project in self.projects.values() if project.user_id == user_id)

    async def exists_by_name(
        self,
        user_id: int,
        name: str,
        exclude_project_id: int | None = None,
    ) -> bool:
        return any(
            project.user_id == user_id
            and project.name == name
            and (
                exclude_project_id is None or project.id != exclude_project_id
            )
            for project in self.projects.values()
        )

    async def get_by_id_for_user(self, project_id: int, user_id: int) -> Project | None:
        project = self.projects.get(project_id)
        if project is None:
            return None
        if project.user_id != user_id:
            return None
        return project

    async def get_by_id(self, project_id: int) -> Project | None:
        return self.projects.get(project_id)

    async def insert(self, project: Project) -> Project:
        self.projects[project.id] = project
        return project

    async def delete(self, project: Project) -> None:
        self.projects.pop(project.id, None)

    async def update_name(self, project_id: int, name: str) -> Project:
        project = self.projects[project_id]
        project.name = name
        return project

    async def list_by_user(
        self,
        user_id: int,
        limit: int,
        cursor: int | None = None,
    ) -> list[Project]:
        projects = [project for project in self.projects.values() if project.user_id == user_id]
        projects.sort(key=lambda project: project.id)
        if cursor is not None:
            projects = [project for project in projects if project.id > cursor]
        return projects[:limit]

    async def update_resource(
        self,
        project_id: int,
        max_cpu: float | None = None,
        max_memory: float | None = None,
        max_disk: float | None = None,
    ) -> Project:
        project = self.projects[project_id]
        if max_cpu is not None:
            project.max_cpu = max_cpu
        if max_memory is not None:
            project.max_memory = max_memory
        if max_disk is not None:
            project.max_disk = max_disk
        return project

    async def get_by_ids(self, project_ids: list[int]) -> list[Project]:
        ids = list(reversed(project_ids)) if self.reverse_get_by_ids else project_ids
        return [self.projects[project_id] for project_id in ids if project_id in self.projects]


class FakeProjectMemberRepository:
    def __init__(
        self,
        members: list[ProjectMember] | None = None,
        *,
        project_ids_override: dict[int, list[int]] | None = None,
    ) -> None:
        self.members: dict[tuple[int, int], ProjectMember] = {
            (member.project_id, member.user_id): member for member in (members or [])
        }
        self.project_ids_override = project_ids_override or {}

    async def list_by_project(
        self,
        project_id: int,
        limit: int,
        cursor: int | None = None,
    ) -> list[ProjectMember]:
        members = [member for member in self.members.values() if member.project_id == project_id]
        members.sort(key=lambda member: (member.joined_at, member.id))
        if cursor is not None:
            members = [member for member in members if member.id > cursor]
        return members[:limit]

    async def get_by_project_and_user(
        self,
        project_id: int,
        user_id: int,
    ) -> ProjectMember | None:
        return self.members.get((project_id, user_id))

    async def exists_by_project_and_user(
        self,
        project_id: int,
        user_id: int,
    ) -> bool:
        return (project_id, user_id) in self.members

    async def insert(self, member: ProjectMember) -> ProjectMember:
        self.members[(member.project_id, member.user_id)] = member
        return member

    async def delete(self, member: ProjectMember) -> None:
        self.members.pop((member.project_id, member.user_id), None)

    async def is_owner(self, project_id: int, user_id: int) -> bool:
        member = self.members.get((project_id, user_id))
        return member is not None and member.role == "OWNER"

    async def has_access(self, project_id: int, user_id: int) -> bool:
        return (project_id, user_id) in self.members

    async def list_project_ids_by_user(
        self,
        user_id: int,
        limit: int,
        cursor: int | None = None,
    ) -> list[int]:
        if user_id in self.project_ids_override:
            project_ids = list(self.project_ids_override[user_id])
        else:
            project_ids = [
                project_id
                for (project_id, member_user_id) in self.members
                if member_user_id == user_id
            ]
        project_ids.sort()
        if cursor is not None:
            project_ids = [project_id for project_id in project_ids if project_id > cursor]
        return project_ids[:limit]

    async def get_role(self, project_id: int, user_id: int) -> str | None:
        member = self.members.get((project_id, user_id))
        return member.role if member is not None else None

    async def get_roles_batch(
        self,
        project_ids: list[int],
        user_id: int,
    ) -> dict[int, str]:
        return {
            project_id: member.role
            for project_id in project_ids
            if (member := self.members.get((project_id, user_id))) is not None
        }

    async def update_role(
        self,
        project_id: int,
        user_id: int,
        role: str,
    ) -> ProjectMember | None:
        member = self.members.get((project_id, user_id))
        if member is None:
            return None
        member.role = role
        return member


class FakeProjectInvitationRepository:
    def __init__(self, invitations: list[ProjectInvitation] | None = None) -> None:
        self.invitations: dict[int, ProjectInvitation] = {
            invitation.id: invitation for invitation in (invitations or [])
        }

    async def get_pending_by_project_and_user(
        self,
        project_id: int,
        invitee_user_id: int,
    ) -> ProjectInvitation | None:
        for invitation in self.invitations.values():
            if (
                invitation.project_id == project_id
                and invitation.invitee_user_id == invitee_user_id
                and invitation.status == "PENDING"
            ):
                return invitation
        return None

    async def get_pending_by_token_hash(
        self,
        project_id: int,
        token_hash: str,
    ) -> ProjectInvitation | None:
        for invitation in self.invitations.values():
            if (
                invitation.project_id == project_id
                and invitation.token_hash == token_hash
                and invitation.status == "PENDING"
            ):
                return invitation
        return None

    async def get_by_id(
        self,
        project_id: int,
        invitation_id: int,
    ) -> ProjectInvitation | None:
        invitation = self.invitations.get(invitation_id)
        if invitation is None or invitation.project_id != project_id:
            return None
        return invitation

    async def list_by_project(
        self,
        project_id: int,
        status: str | None,
        limit: int,
        cursor: int | None = None,
    ) -> list[ProjectInvitation]:
        invitations = [
            invitation
            for invitation in self.invitations.values()
            if invitation.project_id == project_id
            and (status is None or invitation.status == status)
        ]
        invitations.sort(key=lambda invitation: invitation.id)
        if cursor is not None:
            invitations = [
                invitation for invitation in invitations if invitation.id > cursor
            ]
        return invitations[:limit]

    async def insert(self, invitation: ProjectInvitation) -> ProjectInvitation:
        self.invitations[invitation.id] = invitation
        return invitation

    async def update_status(
        self,
        invitation_id: int,
        status: str,
    ) -> ProjectInvitation | None:
        invitation = self.invitations.get(invitation_id)
        if invitation is None:
            return None
        invitation.status = status
        invitation.responded_at = datetime.now(timezone.utc)
        return invitation

    async def rotate_token(
        self,
        invitation_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> ProjectInvitation | None:
        invitation = self.invitations.get(invitation_id)
        if invitation is None or invitation.status != "PENDING":
            return None
        invitation.token_hash = token_hash
        invitation.expires_at = expires_at
        return invitation


class FakeUnitOfWork:
    def __init__(
        self,
        *,
        project_repo: FakeProjectRepository | None = None,
        project_member_repo: FakeProjectMemberRepository | None = None,
        project_invitation_repo: FakeProjectInvitationRepository | None = None,
    ) -> None:
        self.project = project_repo or FakeProjectRepository()
        self.project_member = project_member_repo or FakeProjectMemberRepository()
        self.project_invitation = project_invitation_repo or FakeProjectInvitationRepository()
        self.enter_count = 0
        self.exit_count = 0
        self.last_exception: BaseException | None = None
        self.commit_count = 0
        self.rollback_count = 0

    async def __aenter__(self) -> "FakeUnitOfWork":
        self.enter_count += 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.exit_count += 1
        self.last_exception = exc_val

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_count += 1


class FakeProjectResourceClient:
    def __init__(self, usage: ProjectResourceSnapshotData | None = None) -> None:
        self.usage = usage or ProjectResourceSnapshotData(
            project_id="",
            cpu=ResourceMetricSnapshotData(
                limit="0",
                used="0",
                percentage=0,
                unit="",
            ),
            memory=ResourceMetricSnapshotData(
                limit="0",
                used="0",
                percentage=0,
                unit="",
            ),
            disk=ResourceMetricSnapshotData(
                limit="0",
                used="0",
                percentage=0,
                unit="",
            ),
            instance=ResourceSnapshotData(
                limit=0,
                used=0,
                percentage=0,
            ),
        )
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def _record(self, name: str, **kwargs: Any) -> None:
        self.calls.append((name, kwargs))

    async def create(self, user_id: int, role: str, project: Project) -> None:
        self._record("create", user_id=user_id, role=role, project=project)

    async def delete(self, user_id: int, role: str, project: Project) -> None:
        self._record("delete", user_id=user_id, role=role, project=project)

    async def allocate(self, user_id: int, role: str, project: Project) -> None:
        self._record("allocate", user_id=user_id, role=role, project=project)

    async def get_usage(
        self,
        project: Project,
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ProjectResourceSnapshotData:
        self._record(
            "get_usage",
            project=project,
            days=days,
            interval_minutes=interval_minutes,
        )
        return self.usage

class FakeApplicationClient:
    def __init__(
        self,
        deployments_by_project: dict[int, list[ApplicationItemData]] | None = None,
        summaries: list[DeploymentSummaryItem] | None = None,
        *,
        delete_error: Exception | None = None,
    ) -> None:
        self.deployments_by_project = deployments_by_project or {}
        self.summary_map = {
            summary.project_id: summary for summary in (summaries or [])
        }
        self.summary_requests: list[list[int]] = []
        self.requests = self.summary_requests  # 하위 호환 별칭
        self.delete_requests: list[dict[str, int | str]] = []
        self.delete_error = delete_error

    async def list_by_project(self, project_id: int, user_id: int = 0, role: str = "") -> list[ApplicationItemData]:
        return list(self.deployments_by_project.get(project_id, []))

    async def get_summary_batch(self, project_ids: list[int], user_id: int = 0, role: str = "") -> list[DeploymentSummaryItem]:
        self.summary_requests.append(list(project_ids))
        return [
            self.summary_map[project_id]
            for project_id in project_ids
            if project_id in self.summary_map
        ]

    async def delete_by_project(self, project_id: int, user_id: int = 0, role: str = "") -> None:
        self.delete_requests.append(
            {"project_id": project_id, "user_id": user_id, "role": role}
        )
        if self.delete_error is not None:
            raise self.delete_error


class FakeUserClient:
    def __init__(self, users: list[UserInfo] | None = None) -> None:
        self.users = {user.user_id: user for user in (users or [])}

    async def get_user(self, user_id: int) -> UserInfo | None:
        return self.users.get(user_id)

    async def exists(self, user_id: int) -> bool:
        return user_id in self.users


class FakeProjectInvitationEmailClient:
    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []

    async def send_project_invitation(
        self,
        *,
        to_email: str,
        project_name: str,
        inviter_user_id: int,
        invite_url: str,
    ) -> None:
        self.sent.append(
            {
                "to_email": to_email,
                "project_name": project_name,
                "inviter_user_id": inviter_user_id,
                "invite_url": invite_url,
            }
        )


class FakeDnsClient:
    def __init__(self, *, delete_error: Exception | None = None) -> None:
        self.delete_requests: list[dict[str, Any]] = []
        self.delete_error = delete_error

    async def delete_by_project(
        self,
        project_id: int,
        user_id: int,
        role: str,
    ) -> None:
        self.delete_requests.append(
            {"project_id": project_id, "user_id": user_id, "role": role}
        )
        if self.delete_error is not None:
            raise self.delete_error
