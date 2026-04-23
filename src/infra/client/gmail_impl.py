import asyncio
import logging
import smtplib
from email.mime.text import MIMEText

from src.app.project.exceptions import ProjectInvitationEmailSendFailed
from src.common.config.gmail import GmailConfig
from src.core.client.email import ProjectInvitationEmailClient

logger = logging.getLogger(__name__)


class GmailProjectInvitationEmailClient(ProjectInvitationEmailClient):
    """Gmail SMTP 기반 프로젝트 초대 메일 클라이언트"""

    def __init__(self, config: GmailConfig):
        self.config = config

    async def send_project_invitation(
        self,
        *,
        to_email: str,
        project_name: str,
        inviter_user_id: int,
        invite_url: str,
    ) -> None:
        if not self.config.username or not self.config.password:
            logger.error(
                "project invitation email send failed: gmail credentials missing smtp_host=%s smtp_port=%s to_email=%s project_name=%s inviter_user_id=%s",
                self.config.smtp_host,
                self.config.smtp_port,
                to_email,
                project_name,
                inviter_user_id,
            )
            raise ProjectInvitationEmailSendFailed()

        logger.info(
            "project invitation email send requested: smtp_host=%s smtp_port=%s to_email=%s project_name=%s inviter_user_id=%s",
            self.config.smtp_host,
            self.config.smtp_port,
            to_email,
            project_name,
            inviter_user_id,
        )
        await asyncio.to_thread(
            self._send,
            to_email=to_email,
            project_name=project_name,
            inviter_user_id=inviter_user_id,
            invite_url=invite_url,
        )

    def _send(
        self,
        *,
        to_email: str,
        project_name: str,
        inviter_user_id: int,
        invite_url: str,
    ) -> None:
        sender = self.config.sender_email or self.config.username
        message = MIMEText(
            "\n".join(
                [
                    f"프로젝트 '{project_name}'에 초대되었습니다.",
                    f"초대한 사용자 ID: {inviter_user_id}",
                    "",
                    "아래 링크에서 초대를 승인하세요.",
                    invite_url,
                ]
            ),
            "plain",
            "utf-8",
        )
        message["Subject"] = f"[MADP] {project_name} 프로젝트 초대"
        message["From"] = sender
        message["To"] = to_email

        try:
            with smtplib.SMTP_SSL(
                self.config.smtp_host,
                self.config.smtp_port,
            ) as smtp:
                smtp.login(self.config.username, self.config.password)
                smtp.sendmail(sender, [to_email], message.as_string())
        except Exception as exc:
            logger.exception(
                "project invitation email send failed: smtp request failed smtp_host=%s smtp_port=%s to_email=%s project_name=%s inviter_user_id=%s",
                self.config.smtp_host,
                self.config.smtp_port,
                to_email,
                project_name,
                inviter_user_id,
            )
            raise ProjectInvitationEmailSendFailed() from exc
