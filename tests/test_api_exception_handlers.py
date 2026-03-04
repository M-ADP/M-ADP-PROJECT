import json

import pytest
from fastapi import FastAPI
from starlette.requests import Request

from src.api import create_app
from src.core.exceptions import AppException, register_exception_handlers


pytestmark = pytest.mark.anyio


def _request() -> Request:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    return Request(scope)


async def test_app_exception_handler_returns_configured_status_and_message() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    handler = app.exception_handlers[AppException]
    response = await handler(_request(), AppException("잘못된 요청", status_code=409, code="INVALID"))

    assert response.status_code == 409
    assert json.loads(response.body) == {"message": "잘못된 요청"}


async def test_unexpected_exception_handler_returns_500_and_message() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    handler = app.exception_handlers[Exception]
    response = await handler(_request(), RuntimeError("boom"))

    assert response.status_code == 500
    assert json.loads(response.body) == {"message": "boom"}


def test_create_app_registers_exception_handlers() -> None:
    app = create_app()

    assert AppException in app.exception_handlers
    assert Exception in app.exception_handlers
