from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.core.client.deployment import DeploymentItemData
from src.core.client.deployment_summary import DeploymentSummaryItem
from src.core.client.project_resource import MetricPointData, ResourceUsageData
from src.core.client.user import UserInfo
from src.core.domain.dns import DNS, DNSState
from src.core.domain.port import Port
from src.core.domain.project import Project, ProjectMember


def make_project(
    project_id: str,
    *,
    user_id: str = "user-1",
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
    project_id: str,
    user_id: str,
    *,
    member_id: str | None = None,
    role: str = "MEMBER",
    joined_at: datetime | None = None,
) -> ProjectMember:
    return ProjectMember(
        id=member_id or f"m-{project_id}-{user_id}",
        project_id=project_id,
        user_id=user_id,
        role=role,
        joined_at=joined_at or datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


def make_port(
    project_id: str,
    port_id: str,
    *,
    from_ip: str = "0.0.0.0/0",
    from_port: int = 80,
    port_number: int = 6,
    protocol: str = "tcp",
) -> Port:
    return Port(
        id=port_id,
        project_id=project_id,
        from_ip=from_ip,
        from_port=from_port,
        port_number=port_number,
        protocol=protocol,
    )


def make_dns(
    project_id: str,
    dns_id: str,
    *,
    dns_name: str,
    state: DNSState = DNSState.PENDING,
    port_id: str | None = None,
) -> DNS:
    return DNS(
        id=dns_id,
        project_id=project_id,
        dns_name=dns_name,
        state=state,
        port_id=port_id,
    )


class FakeProjectRepository:
    def __init__(
        self,
        projects: list[Project] | None = None,
        *,
        reverse_get_by_ids: bool = False,
    ) -> None:
        self.projects: dict[str, Project] = {
            project.id: project for project in (projects or [])
        }
        self.reverse_get_by_ids = reverse_get_by_ids

    async def count_by_user(self, user_id: str) -> int:
        return sum(1 for project in self.projects.values() if project.user_id == user_id)

    async def exists_by_name(
        self,
        user_id: str,
        name: str,
        exclude_project_id: str | None = None,
    ) -> bool:
        return any(
            project.user_id == user_id
            and project.name == name
            and project.id != exclude_project_id
            for project in self.projects.values()
        )

    async def get_by_id_for_user(self, project_id: str, user_id: str) -> Project | None:
        project = self.projects.get(project_id)
        if project is None:
            return None
        if project.user_id != user_id:
            return None
        return project

    async def get_by_id(self, project_id: str) -> Project | None:
        return self.projects.get(project_id)

    async def insert(self, project: Project) -> Project:
        self.projects[project.id] = project
        return project

    async def delete(self, project: Project) -> None:
        self.projects.pop(project.id, None)

    async def update_name(self, project_id: str, name: str) -> Project:
        project = self.projects[project_id]
        project.name = name
        return project

    async def list_by_user(
        self,
        user_id: str,
        limit: int,
        cursor: str | None = None,
    ) -> list[Project]:
        projects = [project for project in self.projects.values() if project.user_id == user_id]
        projects.sort(key=lambda project: project.id)
        if cursor is not None:
            projects = [project for project in projects if project.id > cursor]
        return projects[:limit]

    async def update_resource(
        self,
        project_id: str,
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

    async def get_by_ids(self, project_ids: list[str]) -> list[Project]:
        ids = list(reversed(project_ids)) if self.reverse_get_by_ids else project_ids
        return [self.projects[project_id] for project_id in ids if project_id in self.projects]


class FakeProjectMemberRepository:
    def __init__(
        self,
        members: list[ProjectMember] | None = None,
        *,
        project_ids_override: dict[str, list[str]] | None = None,
    ) -> None:
        self.members: dict[tuple[str, str], ProjectMember] = {
            (member.project_id, member.user_id): member for member in (members or [])
        }
        self.project_ids_override = project_ids_override or {}

    async def list_by_project(
        self,
        project_id: str,
        limit: int,
        cursor: str | None = None,
    ) -> list[ProjectMember]:
        members = [member for member in self.members.values() if member.project_id == project_id]
        members.sort(key=lambda member: (member.joined_at, member.id))
        if cursor is not None:
            members = [member for member in members if member.id > cursor]
        return members[:limit]

    async def get_by_project_and_user(
        self,
        project_id: str,
        user_id: str,
    ) -> ProjectMember | None:
        return self.members.get((project_id, user_id))

    async def exists_by_project_and_user(
        self,
        project_id: str,
        user_id: str,
    ) -> bool:
        return (project_id, user_id) in self.members

    async def insert(self, member: ProjectMember) -> ProjectMember:
        self.members[(member.project_id, member.user_id)] = member
        return member

    async def delete(self, member: ProjectMember) -> None:
        self.members.pop((member.project_id, member.user_id), None)

    async def is_owner(self, project_id: str, user_id: str) -> bool:
        member = self.members.get((project_id, user_id))
        return member is not None and member.role == "OWNER"

    async def has_access(self, project_id: str, user_id: str) -> bool:
        return (project_id, user_id) in self.members

    async def list_project_ids_by_user(
        self,
        user_id: str,
        limit: int,
        cursor: str | None = None,
    ) -> list[str]:
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

    async def get_role(self, project_id: str, user_id: str) -> str | None:
        member = self.members.get((project_id, user_id))
        return member.role if member is not None else None

    async def get_roles_batch(
        self,
        project_ids: list[str],
        user_id: str,
    ) -> dict[str, str]:
        return {
            project_id: member.role
            for project_id in project_ids
            if (member := self.members.get((project_id, user_id))) is not None
        }

    async def update_role(
        self,
        project_id: str,
        user_id: str,
        role: str,
    ) -> ProjectMember | None:
        member = self.members.get((project_id, user_id))
        if member is None:
            return None
        member.role = role
        return member


class FakePortRepository:
    def __init__(self, ports: list[Port] | None = None) -> None:
        self.ports: dict[tuple[str, str], Port] = {
            (port.project_id, port.id): port for port in (ports or [])
        }

    async def exists_by_from_port(
        self,
        project_id: str,
        from_port: int,
        exclude_port_id: str | None = None,
    ) -> bool:
        return any(
            port.project_id == project_id
            and port.from_port == from_port
            and port.id != exclude_port_id
            for port in self.ports.values()
        )

    async def list_by_project(
        self,
        project_id: str,
        limit: int,
        cursor: str | None = None,
    ) -> list[Port]:
        ports = [port for port in self.ports.values() if port.project_id == project_id]
        ports.sort(key=lambda port: port.id)
        if cursor is not None:
            ports = [port for port in ports if port.id > cursor]
        return ports[:limit]

    async def get_by_id_for_project(
        self,
        project_id: str,
        port_id: str,
    ) -> Port | None:
        return self.ports.get((project_id, port_id))

    async def insert(self, port: Port) -> Port:
        self.ports[(port.project_id, port.id)] = port
        return port

    async def delete(self, port: Port) -> None:
        self.ports.pop((port.project_id, port.id), None)

    async def update(
        self,
        project_id: str,
        port_id: str,
        from_ip: str,
        from_port: int,
        port_number: int,
        protocol: str,
    ) -> Port:
        port = self.ports[(project_id, port_id)]
        port.from_ip = from_ip
        port.from_port = from_port
        port.port_number = port_number
        port.protocol = protocol
        return port


class FakeDNSRepository:
    def __init__(self, dns_records: list[DNS] | None = None) -> None:
        self.dns_records: dict[tuple[str, str], DNS] = {
            (dns.project_id, dns.id): dns for dns in (dns_records or [])
        }

    async def exists_by_dns_name(
        self,
        dns_name: str,
        exclude_dns_id: str | None = None,
    ) -> bool:
        return any(
            dns.dns_name == dns_name and dns.id != exclude_dns_id
            for dns in self.dns_records.values()
        )

    async def exists_by_project(self, project_id: str) -> bool:
        return any(key[0] == project_id for key in self.dns_records)

    async def get_by_project(self, project_id: str) -> DNS | None:
        records = [dns for dns in self.dns_records.values() if dns.project_id == project_id]
        if not records:
            return None
        records.sort(key=lambda dns: dns.id)
        return records[0]

    async def get_by_id_for_project(self, dns_id: str, project_id: str) -> DNS | None:
        return self.dns_records.get((project_id, dns_id))

    async def insert(self, dns: DNS) -> DNS:
        self.dns_records[(dns.project_id, dns.id)] = dns
        return dns

    async def delete(self, dns: DNS) -> None:
        self.dns_records.pop((dns.project_id, dns.id), None)

    async def update_name(
        self,
        dns_id: str,
        project_id: str,
        dns_name: str,
    ) -> DNS:
        dns = self.dns_records[(project_id, dns_id)]
        dns.dns_name = dns_name
        return dns

    async def bind_port(
        self,
        dns_id: str,
        project_id: str,
        port_id: str,
    ) -> DNS:
        dns = self.dns_records[(project_id, dns_id)]
        dns.port_id = port_id
        return dns


class FakeUnitOfWork:
    def __init__(
        self,
        *,
        project_repo: FakeProjectRepository | None = None,
        project_member_repo: FakeProjectMemberRepository | None = None,
        port_repo: FakePortRepository | None = None,
        dns_repo: FakeDNSRepository | None = None,
    ) -> None:
        self.project = project_repo or FakeProjectRepository()
        self.project_member = project_member_repo or FakeProjectMemberRepository()
        self.port = port_repo or FakePortRepository()
        self.dns = dns_repo or FakeDNSRepository()
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
    def __init__(self, usage: ResourceUsageData | None = None) -> None:
        self.usage = usage or ResourceUsageData()
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def _record(self, name: str, **kwargs: Any) -> None:
        self.calls.append((name, kwargs))

    async def create(self, user_id: str, project: Project) -> None:
        self._record("create", user_id=user_id, project=project)

    async def delete(self, user_id: str, project: Project) -> None:
        self._record("delete", user_id=user_id, project=project)

    async def open_port(self, user_id: str, project: Project, port: Port) -> None:
        self._record("open_port", user_id=user_id, project=project, port=port)

    async def close_port(self, user_id: str, project: Project, port: Port) -> None:
        self._record("close_port", user_id=user_id, project=project, port=port)

    async def update_port(
        self,
        user_id: str,
        project: Project,
        original_port: Port,
        updated_port: Port,
    ) -> None:
        self._record(
            "update_port",
            user_id=user_id,
            project=project,
            original_port=original_port,
            updated_port=updated_port,
        )

    async def allocate(self, user_id: str, project: Project) -> None:
        self._record("allocate", user_id=user_id, project=project)

    async def get_usage(
        self,
        project: Project,
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ResourceUsageData:
        self._record(
            "get_usage",
            project=project,
            days=days,
            interval_minutes=interval_minutes,
        )
        return self.usage

    async def create_dns(self) -> None:
        self._record("create_dns")

    async def delete_dns(self) -> None:
        self._record("delete_dns")

    async def update_dns(self) -> None:
        self._record("update_dns")

    async def mapping_dns_and_port(self) -> None:
        self._record("mapping_dns_and_port")


@dataclass
class FakeDeploymentClient:
    deployments_by_project: dict[str, list[DeploymentItemData]]

    async def list_by_project(self, project_id: str) -> list[DeploymentItemData]:
        return list(self.deployments_by_project.get(project_id, []))


class FakeDeploymentSummaryClient:
    def __init__(self, summaries: list[DeploymentSummaryItem] | None = None) -> None:
        self.summary_map = {
            summary.project_id: summary for summary in (summaries or [])
        }
        self.requests: list[list[str]] = []

    async def get_summary_batch(self, project_ids: list[str]) -> list[DeploymentSummaryItem]:
        self.requests.append(list(project_ids))
        return [
            self.summary_map[project_id]
            for project_id in project_ids
            if project_id in self.summary_map
        ]


class FakeUserClient:
    def __init__(self, users: list[UserInfo] | None = None) -> None:
        self.users = {user.user_id: user for user in (users or [])}

    async def get_user(self, user_id: str) -> UserInfo | None:
        return self.users.get(user_id)

    async def exists(self, user_id: str) -> bool:
        return user_id in self.users


def single_metric(value: float, *, ts: str = "2026-01-01T00:00:00Z") -> list[MetricPointData]:
    return [MetricPointData(timestamp=ts, value=value)]
