import pytest

from src.common.config.application_server import ApplicationServerConfig
from src.core.exceptions import ApplicationServerException
from src.infra.client.application_impl import ApplicationClientImpl


class StubResponse:
    def __init__(self, *, status: int = 200, payload=None, text_body: str = "") -> None:
        self.status = status
        self._payload = payload if payload is not None else {"data": []}
        self._text_body = text_body

    async def json(self, content_type=None):
        return self._payload

    async def text(self) -> str:
        return self._text_body

    def release(self) -> None:
        return None


class RecordingHttpClient:
    def __init__(self) -> None:
        self.get_calls: list[dict] = []
        self.post_calls: list[dict] = []
        self.delete_calls: list[dict] = []
        self.delete_response = StubResponse(status=204, payload=None)

    async def get(self, path, params=None, headers=None):
        self.get_calls.append(
            {"path": path, "params": params, "headers": headers}
        )
        return StubResponse(
            payload={
                "data": [
                    {
                        "id": 1,
                        "name": "web",
                        "pod_count": 2,
                        "exposed_port": 8080,
                        "cpu_usage_percent": 12.5,
                        "ram_usage_percent": 45.0,
                        "health_status": "RUNNING",
                    }
                ]
            }
        )

    async def post(self, path, data=None, json=None, headers=None):
        self.post_calls.append(
            {"path": path, "data": data, "json": json, "headers": headers}
        )
        return StubResponse(
            payload={
                "data": [
                    {
                        "project_id": 101,
                        "running": 1,
                        "warning": 0,
                        "state": "RUNNING",
                    }
                ]
            }
        )

    async def delete(self, *args, **kwargs):
        self.delete_calls.append({"args": args, "kwargs": kwargs})
        return self.delete_response

    async def put(self, *args, **kwargs):
        raise NotImplementedError

    async def patch(self, *args, **kwargs):
        raise NotImplementedError


pytestmark = pytest.mark.anyio


async def test_list_by_project_uses_latest_application_path_contract() -> None:
    http_client = RecordingHttpClient()
    client = ApplicationClientImpl(
        config=ApplicationServerConfig(),
        http_client=http_client,
    )

    items = await client.list_by_project(project_id=101, user_id=7, role="USER")

    assert items[0].id == 1
    assert http_client.get_calls == [
        {
            "path": "/apps/projects/101/apps",
            "params": None,
            "headers": {"X-User-Id": "7", "X-User-Role": "USER"},
        }
    ]


async def test_get_summary_batch_uses_latest_application_summary_path() -> None:
    http_client = RecordingHttpClient()
    client = ApplicationClientImpl(
        config=ApplicationServerConfig(),
        http_client=http_client,
    )

    items = await client.get_summary_batch(project_ids=[101], user_id=7, role="USER")

    assert items[0].project_id == 101
    assert http_client.post_calls == [
        {
            "path": "/apps/summary",
            "data": None,
            "json": {"project_ids": [101]},
            "headers": {"X-User-Id": "7", "X-User-Role": "USER"},
        }
    ]


async def test_delete_by_project_uses_latest_application_delete_path_contract() -> None:
    http_client = RecordingHttpClient()
    client = ApplicationClientImpl(
        config=ApplicationServerConfig(),
        http_client=http_client,
    )

    await client.delete_by_project(project_id=101, user_id=7, role="USER")

    assert http_client.delete_calls == [
        {
            "args": ("/apps/projects/101/apps",),
            "kwargs": {"params": None, "headers": {"X-User-Id": "7", "X-User-Role": "USER"}},
        }
    ]


async def test_delete_by_project_raises_when_status_is_not_204() -> None:
    http_client = RecordingHttpClient()
    http_client.delete_response = StubResponse(status=200, payload=None, text_body="unexpected")
    client = ApplicationClientImpl(
        config=ApplicationServerConfig(),
        http_client=http_client,
    )

    with pytest.raises(ApplicationServerException):
        await client.delete_by_project(project_id=101, user_id=7, role="USER")
