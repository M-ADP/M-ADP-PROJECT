from src.core.client.user import UserClient, UserInfo


class FakeUserClientImpl(UserClient):

    async def get_user(self, user_id: int) -> UserInfo | None:
        return UserInfo(user_id=user_id, username=f"user-{user_id}")

    async def exists(self, user_id: int) -> bool:
        return True
