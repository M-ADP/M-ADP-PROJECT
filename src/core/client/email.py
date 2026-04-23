from abc import ABC, abstractmethod


class ProjectInvitationEmailClient(ABC):
    @abstractmethod
    async def send_project_invitation(
        self,
        *,
        to_email: str,
        project_name: str,
        inviter_user_id: int,
        invite_url: str,
    ) -> None:
        """프로젝트 초대 메일을 발송합니다."""
        ...
