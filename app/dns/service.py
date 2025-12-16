from sqlalchemy.ext.asyncio import AsyncSession

from app.dns.models import DNS, DNSState
from app.dns.schemas import DNSCreate, DNSUpdate
from app.dns.exceptions import DNSNameAlreadyExists, DNSNotFound, ProjectAlreadyHasDNS
from app.dns import repository as dns_repository
from app.project import repository as project_repository
from app.project.exceptions import ProjectNotFound
from core.id_generator import generate_sonyflake_id

DNS_DOMAIN = "mdeveloper.platform"


async def create_dns_for_project(
    project_id: str,
    request: DNSCreate,
    user_id: str,
    session: AsyncSession,
) -> DNS:
    """프로젝트에 DNS를 생성합니다."""
    # 프로젝트 확인
    project = await project_repository.get_by_id_for_user(session, project_id, user_id)
    if project is None:
        raise ProjectNotFound()

    # 프로젝트에 이미 DNS가 있는지 확인
    if await dns_repository.exists_by_project(session, project_id):
        raise ProjectAlreadyHasDNS()

    # DNS 이름 생성
    dns_name = f"{request.subdomain}.{DNS_DOMAIN}"

    # DNS 이름 중복 체크
    if await dns_repository.exists_by_dns_name(session, dns_name):
        raise DNSNameAlreadyExists()

    # 새 DNS 생성
    dns_id = generate_sonyflake_id()
    dns = DNS(
        id=dns_id,
        project_id=project_id,
        dns_name=dns_name,
        state=DNSState.PENDING,
    )
    dns = await dns_repository.insert(session, dns)

    return dns


async def get_dns_for_project(
    project_id: str,
    user_id: str,
    session: AsyncSession,
) -> DNS | None:
    """프로젝트의 DNS를 조회합니다."""
    project = await project_repository.get_by_id_for_user(session, project_id, user_id)
    if project is None:
        raise ProjectNotFound()

    dns = await dns_repository.get_by_project(session, project_id)
    return dns


async def delete_dns_from_project(
    project_id: str,
    dns_id: str,
    user_id: str,
    session: AsyncSession,
) -> DNS:
    """프로젝트의 DNS를 삭제합니다."""
    project = await project_repository.get_by_id_for_user(session, project_id, user_id)
    if project is None:
        raise ProjectNotFound()

    dns = await dns_repository.get_by_id_for_project(session, dns_id, project_id)
    if dns is None:
        raise DNSNotFound()

    # DNS 삭제
    await dns_repository.delete(session, dns)

    return dns


async def update_dns_for_project(
    project_id: str,
    dns_id: str,
    request: DNSUpdate,
    user_id: str,
    session: AsyncSession,
) -> DNS:
    """프로젝트의 DNS 서브도메인을 업데이트합니다."""
    project = await project_repository.get_by_id_for_user(session, project_id, user_id)
    if project is None:
        raise ProjectNotFound()

    dns = await dns_repository.get_by_id_for_project(session, dns_id, project_id)
    if dns is None:
        raise DNSNotFound()

    # 새 DNS 이름 생성
    new_dns_name = f"{request.subdomain}.{DNS_DOMAIN}"

    # DNS 이름 중복 체크 (현재 DNS ID 제외)
    if await dns_repository.exists_by_dns_name(session, new_dns_name, exclude_dns_id=dns_id):
        raise DNSNameAlreadyExists()

    # DNS 이름 업데이트
    dns.dns_name = new_dns_name
    await session.flush()

    return dns
