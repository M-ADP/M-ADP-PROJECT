from sqlalchemy.ext.asyncio import AsyncSession

from src.app.dns.models import DNS
from src.app.dns.schemas import DNSPortBinding
from src.app.dns.exceptions import DNSNotFound
from src.app.dns import repository as dns_repository
from src.app.project import repository as project_repository
from src.app.project.exceptions import ProjectNotFound
from src.app.port import repository as port_repository
from src.app.port.exceptions import PortNotFound


class BindPortToDNSUseCase:
    """DNS에 공개 포트를 바인딩하는 유즈케이스"""

    async def __call__(
        self,
        project_id: str,
        dns_id: str,
        request: DNSPortBinding,
        user_id: str,
        session: AsyncSession,
    ) -> DNS:
        # 프로젝트 확인
        project = await project_repository.get_by_id_for_user(session, project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        # DNS 확인
        dns = await dns_repository.get_by_id_for_project(session, dns_id, project_id)
        if dns is None:
            raise DNSNotFound()

        # 포트가 해당 프로젝트에 속하는지 확인
        port = await port_repository.get_by_id_for_project(
            session=session,
            project_id=project_id,
            port_id=request.port_id,
        )
        if port is None:
            raise PortNotFound()

        # DNS에 포트 바인딩
        dns.bind_port(request.port_id)
        await session.flush()

        return dns
