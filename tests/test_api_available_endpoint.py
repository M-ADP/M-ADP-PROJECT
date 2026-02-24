import json

import pytest

from src.api.routers.v1.projects import check_project_available_endpoint
from src.dependencies.auth import UserInfo


class StubAvailableUseCase:
    def __init__(self, result: bool) -> None:
        self.result = result
        self.calls: list[tuple[str, str]] = []

    async def __call__(self, project_id: str, user_id: str) -> bool:
        self.calls.append((project_id, user_id))
        return self.result


pytestmark = pytest.mark.anyio


async def test_available_returns_status_true_when_user_has_access() -> None:
    usecase = StubAvailableUseCase(result=True)

    response = await check_project_available_endpoint(
        project_id="p-1",
        user=UserInfo(user_id="u-1", role="MEMBER"),
        usecase=usecase,
    )

    assert response.status_code == 200
    assert json.loads(response.body) == {"status": True}
    assert isinstance(json.loads(response.body)["status"], bool)
    assert usecase.calls == [("p-1", "u-1")]


async def test_available_returns_status_false_with_403_when_user_has_no_access() -> None:
    usecase = StubAvailableUseCase(result=False)

    response = await check_project_available_endpoint(
        project_id="p-2",
        user=UserInfo(user_id="u-2", role="MEMBER"),
        usecase=usecase,
    )

    assert response.status_code == 403
    assert json.loads(response.body) == {"status": False}
    assert isinstance(json.loads(response.body)["status"], bool)
    assert usecase.calls == [("p-2", "u-2")]
