from src.core.client.user import UserClient
from src.common.config.user_server import get_user_server_config
from src.infra.client.user_impl import UserClientImpl


def get_user_client() -> UserClient:
    return UserClientImpl(user_server_config=get_user_server_config())
