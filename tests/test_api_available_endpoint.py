import pytest

from src.api.routers.routes.projects import (
    check_project_available_endpoint,
    check_project_owner_endpoint,
)
from src.dependencies.auth import UserInfo


class StubAvailableUseCase:
    def __init__(self, result: bool) -> None:
        self.result = result
        self.calls: list[tuple[int, int]] = []

    async def __call__(self, project_id: int, user_id: int) -> bool:
        self.calls.append((project_id, user_id))
        return self.result


pytestmark = pytest.mark.anyio


async def test_available_returns_status_true_when_user_has_access() -> None:
    usecase = StubAvailableUseCase(result=True)

    response = await check_project_available_endpoint(
        project_id=1,
        user=UserInfo(user_id=1, role="MEMBER"),
        usecase=usecase,
    )

    assert response.message == "프로젝트 접근 가능 여부를 조회했습니다."
    assert response.data.status is True
    assert usecase.calls == [(1, 1)]


async def test_available_returns_status_false_when_user_has_no_access() -> None:
    usecase = StubAvailableUseCase(result=False)

    response = await check_project_available_endpoint(
        project_id=2,
        user=UserInfo(user_id=2, role="MEMBER"),
        usecase=usecase,
    )

    assert response.message == "프로젝트 접근 가능 여부를 조회했습니다."
    assert response.data.status is False
    assert usecase.calls == [(2, 2)]


async def test_owner_endpoint_uses_header_user_id_instead_of_query_user_id() -> None:
    usecase = StubAvailableUseCase(result=True)

    response = await check_project_owner_endpoint(
        project_id=10,
        user=UserInfo(user_id=777, role="OWNER"),
        usecase=usecase,
    )

    assert response.message == "프로젝트 소유자 여부를 조회했습니다."
    assert response.data.status is True
    assert usecase.calls == [(10, 777)]
