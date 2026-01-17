from src.core.exceptions import AppException


class ProjectLimitExceeded(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 생성 한도(3개)를 초과했습니다.",
            code="PROJECT_LIMIT_EXCEEDED",
        )

class ProjectNameAlreadyExists(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 이름은 고유해야 합니다.",
            code="PROJECT_NAME_EXISTS",
        )


class ProjectNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트를 찾을 수 없습니다.",
            code="PROJECT_NOT_FOUND",
            status_code=404,
        )
