from typing import Any, Optional

from fastapi import FastAPI, status
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.common.schemas import ErrorResponse


class ResourceServerException(Exception):
    def __init__(self, message: str = "리소스 서버와 통신 중 오류가 발생했습니다.") -> None:
        super().__init__(message)
        self.message = message


class ApplicationServerException(Exception):
    def __init__(self, message: str = "앱 배포 서비스와 통신 중 오류가 발생했습니다.") -> None:
        super().__init__(message)
        self.message = message


class DnsServerException(Exception):
    def __init__(self, message: str = "DNS 서버와 통신 중 오류가 발생했습니다.") -> None:
        super().__init__(message)
        self.message = message


class MonitoringServerException(Exception):
    def __init__(self, message: str = "모니터링 서버와 통신 중 오류가 발생했습니다.") -> None:
        super().__init__(message)
        self.message = message


class AppException(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details

    def to_response(self) -> ErrorResponse:
        return ErrorResponse(message=self.message)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        error_response = exc.to_response()
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(_: Request, exc: Exception) -> JSONResponse:
        error = ErrorResponse(message=str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error.model_dump(),
        )
