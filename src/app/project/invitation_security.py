import hashlib
import hmac

from src.common.config.gmail import get_gmail_config


def hash_invitation_token(token: str) -> str:
    secret = get_gmail_config().invitation_token_secret.encode("utf-8")
    return hmac.new(secret, token.encode("utf-8"), hashlib.sha256).hexdigest()
