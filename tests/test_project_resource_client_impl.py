import pytest

from src.common.config.resource_server import ResourceServerConfig
from src.core.domain.project import Project
from src.core.exceptions import ResourceServerException
from src.infra.client.project_resource_impl import ProjectResourceClientImpl


class StubResponse:
    def __init__(self, *, status: int = 200, payload=None) -> None:
        self.status = status
        self._payload = payload if payload is not None else {"data": {}}

    async def json(self, content_type=None):
        return self._payload

    def release(self) -> None:
        return None


class RecordingHttpClient:
    def __init__(self, response: StubResponse | None = None) -> None:
        self.response = response or StubResponse(
            payload={
                "message": "ok",
                "data": {
                    "project_id": "101",
                    "cpu": {"limit": "1000m", "used": "250m", "percentage": 25, "unit": "m"},
                    "memory": {"limit": "1024Mi", "used": "512Mi", "percentage": 50, "unit": "Mi"},
                    "disk": {"limit": "10Gi", "used": "2Gi", "percentage": 20, "unit": "Gi"},
                    "instance": {"limit": 10, "used": 2, "percentage": 20},
                },
            }
        )
        self.get_calls: list[dict] = []

    async def get(self, path, params=None, headers=None):
        self.get_calls.append(
            {"path": path, "params": params, "headers": headers}
        )
        return self.response

    async def post(self, *args, **kwargs):
        raise NotImplementedError

    async def delete(self, *args, **kwargs):
        raise NotImplementedError

    async def put(self, *args, **kwargs):
        raise NotImplementedError

    async def patch(self, *args, **kwargs):
        raise NotImplementedError


pytestmark = pytest.mark.anyio


async def test_get_usage_uses_project_resource_snapshot_path() -> None:
    http_client = RecordingHttpClient()
    client = ProjectResourceClientImpl(
        resource_server_config=ResourceServerConfig(SERVER_BASE_URL="http://localhost:8001"),
        http_client=http_client,
    )

    snapshot = await client.get_usage(Project(id=101, user_id=1, name="alpha"))

    assert snapshot.cpu.used == "250m"
    assert snapshot.instance.used == 2
    assert http_client.get_calls == [
        {
            "path": "http://localhost:8001/projects/101/resource",
            "params": None,
            "headers": None,
        }
    ]


async def test_get_usage_raises_when_status_is_not_200() -> None:
    http_client = RecordingHttpClient(response=StubResponse(status=500))
    client = ProjectResourceClientImpl(
        resource_server_config=ResourceServerConfig(SERVER_BASE_URL="http://localhost:8001"),
        http_client=http_client,
    )

    with pytest.raises(ResourceServerException):
        await client.get_usage(Project(id=101, user_id=1, name="alpha"))
