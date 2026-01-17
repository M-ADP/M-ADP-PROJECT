from src.core.exceptions import AppException


class PortAlreadyExists(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 내에서 이미 사용 중인 포트입니다.",
            code="PROJECT_PORT_EXISTS",
        )


class PortNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            "포트를 찾을 수 없습니다.",
            code="PORT_NOT_FOUND",
            status_code=404,
        )
