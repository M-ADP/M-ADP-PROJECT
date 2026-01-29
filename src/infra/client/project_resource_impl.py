from src.common.client.project_resource import ProjectResourceClient, ResourceUsageData


class MockProjectResourceClient(ProjectResourceClient):
    """프로젝트 리소스 접근 Mock 클라이언트"""

    async def create(self) -> None:
        print("namespace 생성")
        return None

    async def delete(self) -> None:
        print("namespace 삭제")
        return None

    async def open_port(self) -> None:
        print("gateway 자원 생성")
        return None

    async def close_port(self) -> None:
        print("gateway 자원 삭제")
        return None

    async def update_port(self) -> None:
        print("gateway 자원 수정")
        return None

    async def create_dns(self) -> None:
        print("ExternalDNS 자원 생성")
        return None

    async def delete_dns(self) -> None:
        print("ExternalDNS 자원 삭제")
        return None

    async def update_dns(self) -> None:
        print("ExternalDNS 자원 수정")
        return None

    async def mapping_dns_and_port(self) -> None:
        print("ExternalDNS 자원과 gateway 자원 매핑")
        return None

    async def allocate(self) -> None:
        print("Resource Quota 자원 생성")
        return None

    async def get_usage(
        self,
        project_id: str,
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ResourceUsageData:
        print(
            f"프로젝트 {project_id} 최근 {days}일 리소스 사용량 조회 "
            f"(간격 {interval_minutes}분)"
        )
        return ResourceUsageData()
