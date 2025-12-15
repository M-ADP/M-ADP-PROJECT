from core.exceptions import AppException


class PortAlreadyExists(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 내에서 이미 사용 중인 포트입니다.",
            code="PROJECT_PORT_EXISTS",
        )
