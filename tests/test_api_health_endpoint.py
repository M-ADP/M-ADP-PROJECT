from src.api.routers.health import health_check


def test_health_endpoint_contract() -> None:
    # health 엔드포인트는 순수 딕셔너리 응답 계약을 유지한다.
    result = __import__("asyncio").run(health_check())

    assert result == {
        "status": "healthy",
        "service": "MADP Project Service",
    }
