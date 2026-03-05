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


# ===== Resource Server Exceptions =====


class PortCreationFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            "리소스 서버 오류로 포트를 생성할 수 없습니다.",
            code="PORT_CREATION_FAILED",
            status_code=502,
        )


class PortDeletionFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            "리소스 서버 오류로 포트를 삭제할 수 없습니다.",
            code="PORT_DELETION_FAILED",
            status_code=502,
        )


class PortUpdateFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            "리소스 서버 오류로 포트를 변경할 수 없습니다.",
            code="PORT_UPDATE_FAILED",
            status_code=502,
        )
