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


class DiskCannotBeReduced(AppException):
    def __init__(self) -> None:
        super().__init__(
            "디스크 용량은 줄일 수 없습니다.",
            code="DISK_CANNOT_BE_REDUCED",
            status_code=400,
        )


class InvalidPassword(AppException):
    def __init__(self) -> None:
        super().__init__(
            "비밀번호가 올바르지 않습니다.",
            code="INVALID_PASSWORD",
            status_code=401,
        )


# ===== Project Member Exceptions =====


class MemberAlreadyExists(AppException):
    def __init__(self) -> None:
        super().__init__(
            "이미 프로젝트에 참여 중인 사용자입니다.",
            code="MEMBER_ALREADY_EXISTS",
            status_code=400,
        )


class MemberNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            "멤버를 찾을 수 없습니다.",
            code="MEMBER_NOT_FOUND",
            status_code=404,
        )


class CannotRemoveOwner(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 소유자는 제거할 수 없습니다.",
            code="CANNOT_REMOVE_OWNER",
            status_code=400,
        )


class OnlyOwnerCanAddMembers(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 소유자만 멤버를 추가할 수 있습니다.",
            code="ONLY_OWNER_CAN_ADD_MEMBERS",
            status_code=403,
        )


class OnlyOwnerCanRemoveMembers(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 소유자만 멤버를 제거할 수 있습니다.",
            code="ONLY_OWNER_CAN_REMOVE_MEMBERS",
            status_code=403,
        )


class UserNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            "사용자를 찾을 수 없습니다.",
            code="USER_NOT_FOUND",
            status_code=404,
        )
