from src.common.client.user import UserClient
from src.infra.client.user_impl import MockUserClient


def get_user_client() -> UserClient:
    return MockUserClient()
