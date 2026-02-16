from src.core.client.user import UserClient, UserInfo


class MockUserClient(UserClient):
    """사용자 서비스 Mock 클라이언트"""

    # Mock 데이터: 존재하는 사용자 목록
    _mock_users: dict[str, UserInfo] = {
        "user1": UserInfo(
            user_id="user1",
            username="사용자1",
            profile_image="https://example.com/user1.png",
        ),
        "user2": UserInfo(
            user_id="user2",
            username="사용자2",
            profile_image=None,
        ),
        "user3": UserInfo(
            user_id="user3",
            username="사용자3",
            profile_image="https://example.com/user3.png",
        ),
    }

    async def get_user(self, user_id: str) -> UserInfo | None:
        print(f"사용자 {user_id} 정보 조회")
        return self._mock_users.get(user_id)

    async def exists(self, user_id: str) -> bool:
        print(f"사용자 {user_id} 존재 여부 확인")
        return user_id in self._mock_users

    async def verify_password(self, user_id: str, password: str) -> bool:
        print(f"사용자 {user_id} 비밀번호 검증")
        return True
