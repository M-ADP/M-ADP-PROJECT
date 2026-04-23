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


class OnlyOwnerCanDeleteProject(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 소유자만 프로젝트를 삭제할 수 있습니다.",
            code="ONLY_OWNER_CAN_DELETE_PROJECT",
            status_code=403,
        )


class OnlyOwnerCanUpdateResource(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 소유자만 리소스를 변경할 수 있습니다.",
            code="ONLY_OWNER_CAN_UPDATE_RESOURCE",
            status_code=403,
        )


class OnlyOwnerCanGetResourceLimit(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 소유자만 리소스 한도를 조회할 수 있습니다.",
            code="ONLY_OWNER_CAN_GET_RESOURCE_LIMIT",
            status_code=403,
        )


class OnlyOwnerCanUpdateProjectName(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 소유자만 프로젝트 이름을 변경할 수 있습니다.",
            code="ONLY_OWNER_CAN_UPDATE_PROJECT_NAME",
            status_code=403,
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


class MemberInvitationAlreadyExists(AppException):
    def __init__(self) -> None:
        super().__init__(
            "이미 대기 중인 프로젝트 초대가 있습니다.",
            code="MEMBER_INVITATION_ALREADY_EXISTS",
            status_code=400,
        )


class InvitationNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            "초대를 찾을 수 없습니다.",
            code="INVITATION_NOT_FOUND",
            status_code=404,
        )


class InvitationTargetMismatch(AppException):
    def __init__(self) -> None:
        super().__init__(
            "초대 대상 사용자만 초대를 승인할 수 있습니다.",
            code="INVITATION_TARGET_MISMATCH",
            status_code=403,
        )


class InvitationExpired(AppException):
    def __init__(self) -> None:
        super().__init__(
            "만료된 초대입니다.",
            code="INVITATION_EXPIRED",
            status_code=400,
        )


class CannotCancelInvitation(AppException):
    def __init__(self) -> None:
        super().__init__(
            "대기 중인 초대만 취소할 수 있습니다.",
            code="CANNOT_CANCEL_INVITATION",
            status_code=400,
        )


class CannotResendInvitation(AppException):
    def __init__(self) -> None:
        super().__init__(
            "대기 중인 초대만 재발송할 수 있습니다.",
            code="CANNOT_RESEND_INVITATION",
            status_code=400,
        )


class UserEmailNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            "사용자의 인증된 이메일을 찾을 수 없습니다.",
            code="USER_EMAIL_NOT_FOUND",
            status_code=400,
        )


class ProjectInvitationEmailSendFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 초대 메일 발송에 실패했습니다.",
            code="PROJECT_INVITATION_EMAIL_SEND_FAILED",
            status_code=500,
        )


class OnlyOwnerCanTransferOwnership(AppException):
    def __init__(self) -> None:
        super().__init__(
            "프로젝트 소유자만 소유권을 이전할 수 있습니다.",
            code="ONLY_OWNER_CAN_TRANSFER_OWNERSHIP",
            status_code=403,
        )


class OwnershipTransferTargetMustBeMember(AppException):
    def __init__(self) -> None:
        super().__init__(
            "소유권은 MEMBER 멤버에게만 이전할 수 있습니다.",
            code="OWNERSHIP_TRANSFER_TARGET_MUST_BE_MEMBER",
            status_code=400,
        )


class CannotTransferOwnershipToSelf(AppException):
    def __init__(self) -> None:
        super().__init__(
            "자기 자신에게 소유권을 이전할 수 없습니다.",
            code="CANNOT_TRANSFER_OWNERSHIP_TO_SELF",
            status_code=400,
        )


# ===== Resource Server Exceptions =====


class ProjectCreationFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            "리소스 서버 오류로 프로젝트를 생성할 수 없습니다.",
            code="PROJECT_CREATION_FAILED",
            status_code=500,
        )


class ProjectDeletionFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            "연관 앱 삭제에 실패하여 프로젝트를 삭제할 수 없습니다.",
            code="PROJECT_DELETION_FAILED",
            status_code=500,
        )


class ProjectResourceUpdateFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            "리소스 서버 오류로 프로젝트 리소스를 변경할 수 없습니다.",
            code="PROJECT_RESOURCE_UPDATE_FAILED",
            status_code=500,
        )
