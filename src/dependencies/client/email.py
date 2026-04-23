from functools import lru_cache

from src.common.config.gmail import get_gmail_config
from src.core.client.email import ProjectInvitationEmailClient
from src.infra.client.gmail_impl import GmailProjectInvitationEmailClient


@lru_cache
def get_project_invitation_email_client() -> ProjectInvitationEmailClient:
    return GmailProjectInvitationEmailClient(config=get_gmail_config())
