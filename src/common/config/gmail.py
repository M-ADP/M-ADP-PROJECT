from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.common.config.settings import register_config
from src.common.const.vault import VAULT_ENV_FILE


class GmailConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MADP_GMAIL_",
        env_file=VAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465
    username: str = ""
    password: str = ""
    sender_email: str = ""
    public_base_url: str = "http://localhost:8000"
    frontend_base_url: str = "http://localhost:3000"
    invitation_token_secret: str = "local-dev-invitation-token-secret"
    invitation_ttl_hours: int = 168


@register_config
@lru_cache
def get_gmail_config() -> GmailConfig:
    return GmailConfig()
