import unittest
from unittest.mock import patch, MagicMock

# Mocking create_all_tables to avoid DB connection
with patch("src.core.db.create_all_tables") as mock_create_tables:
    from src.api import create_app

class TestAppStructure(unittest.TestCase):
    def setUp(self):
        # DB 연결 시도 방지
        self.mock_create_tables = patch("src.core.db.create_all_tables").start()
        
        # 앱 생성 (여기서 에러가 안 나면 의존성 정의는 문제 없는 것)
        self.app = create_app()

    def tearDown(self):
        patch.stopall()

    def test_app_creation(self):
        """앱이 정상적으로 생성되는지 확인"""
        self.assertIsNotNone(self.app)

    def test_routers_registered(self):
        """주요 API 라우터들이 등록되었는지 확인"""
        routes = [route.path for route in self.app.router.routes]
        
        # 라우터 경로 확인 (FastAPI는 /docs, /openapi.json 등도 포함함)
        print("Registered Routes:", routes)

        # 프로젝트 관련 라우터
        self.assertTrue(any("/v1/projects" in r for r in routes), "Project router not registered")
        
        # DNS 관련 라우터
        self.assertTrue(any("/dns" in r for r in routes), "DNS router not registered")
        
        # 포트 관련 라우터
        self.assertTrue(any("/ports" in r for r in routes), "Port router not registered")

if __name__ == "__main__":
    unittest.main()