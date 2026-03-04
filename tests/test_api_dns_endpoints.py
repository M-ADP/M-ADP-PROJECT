import pytest

from src.api.routers.routes.dns import (
    bind_port_to_dns_endpoint,
    create_dns_endpoint,
    delete_dns_endpoint,
    get_dns_endpoint,
    update_dns_endpoint,
)
from src.app.dns.schemas import DNSCreate, DNSPortBinding, DNSResponse, DNSUpdate
from src.core.domain.dns import DNSState
from src.dependencies.auth import UserInfo

from tests.fakes import make_dns


class AsyncUseCaseStub:
    def __init__(self, result):
        self.result = result
        self.calls: list[tuple[tuple, dict]] = []

    async def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.result


pytestmark = pytest.mark.anyio


async def test_create_dns_endpoint_contract() -> None:
    created = make_dns(1, 1, dns_name="app.mdeveloper.platform", state=DNSState.PENDING)
    usecase = AsyncUseCaseStub(created)
    payload = DNSCreate(subdomain="app")

    response = await create_dns_endpoint(
        project_id=1,
        payload=payload,
        user=UserInfo(user_id="u1", role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "DNS가 생성되었습니다."
    assert response.data.id == 1
    assert response.data.dns_name == "app.mdeveloper.platform"
    assert usecase.calls == [((1, payload), {"user_id": "u1"})]


async def test_get_dns_endpoint_contract_with_data() -> None:
    found = make_dns(1, 1, dns_name="app.mdeveloper.platform", state=DNSState.ACTIVE)
    usecase = AsyncUseCaseStub(found)

    response = await get_dns_endpoint(
        project_id=1,
        user=UserInfo(user_id="u1", role="MEMBER"),
        usecase=usecase,
    )

    assert response.message == "DNS를 조회했습니다."
    assert response.data is not None
    assert response.data.dns_name == "app.mdeveloper.platform"
    assert usecase.calls == [((1,), {"user_id": "u1"})]


async def test_get_dns_endpoint_contract_without_data() -> None:
    usecase = AsyncUseCaseStub(None)

    response = await get_dns_endpoint(
        project_id=1,
        user=UserInfo(user_id="u1", role="MEMBER"),
        usecase=usecase,
    )

    assert response.message == "DNS를 조회했습니다."
    assert response.data is None
    assert usecase.calls == [((1,), {"user_id": "u1"})]


async def test_delete_dns_endpoint_contract() -> None:
    deleted = make_dns(1, 1, dns_name="app.mdeveloper.platform", state=DNSState.ACTIVE)
    usecase = AsyncUseCaseStub(deleted)

    response = await delete_dns_endpoint(
        project_id=1,
        dns_id=1,
        user=UserInfo(user_id="u1", role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "DNS가 삭제되었습니다."
    assert response.data.id == 1
    assert usecase.calls == [((1, 1), {"user_id": "u1"})]


async def test_update_dns_endpoint_contract() -> None:
    updated = make_dns(1, 1, dns_name="new.mdeveloper.platform", state=DNSState.ACTIVE)
    usecase = AsyncUseCaseStub(updated)
    payload = DNSUpdate(subdomain="new")

    response = await update_dns_endpoint(
        project_id=1,
        dns_id=1,
        payload=payload,
        user=UserInfo(user_id="u1", role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "DNS가 업데이트되었습니다."
    assert response.data.dns_name == "new.mdeveloper.platform"
    assert usecase.calls == [((1, 1, payload), {"user_id": "u1"})]


async def test_bind_port_to_dns_endpoint_contract() -> None:
    bound = make_dns(
        1,
        1,
        dns_name="app.mdeveloper.platform",
        state=DNSState.ACTIVE,
        port_id=1,
    )
    usecase = AsyncUseCaseStub(bound)
    payload = DNSPortBinding(port_id=1)

    response = await bind_port_to_dns_endpoint(
        project_id=1,
        dns_id=1,
        payload=payload,
        user=UserInfo(user_id="u1", role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "DNS에 포트가 바인딩되었습니다."
    assert response.data.port_id == 1
    assert usecase.calls == [((1, 1, payload), {"user_id": "u1"})]
