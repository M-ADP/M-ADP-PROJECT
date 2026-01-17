from src.core.exceptions import AppException


class DNSNameAlreadyExists(AppException):
    def __init__(self) -> None:
        super().__init__(
            "이미 사용 중인 DNS 이름입니다.",
            code="DNS_NAME_EXISTS",
        )


class DNSNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            "DNS를 찾을 수 없습니다.",
            code="DNS_NOT_FOUND",
            status_code=404,
        )


class ProjectAlreadyHasDNS(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트에 이미 DNS가 등록되어 있습니다.",
            code="PROJECT_ALREADY_HAS_DNS",
        )
