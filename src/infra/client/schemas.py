from typing import Literal, Optional

from pydantic import BaseModel, Field


class ExternalProjectCreate(BaseModel):
    id: str = Field(..., description="프로젝트 ID")
    name: str = Field(..., description="프로젝트 이름")
    cpu: str | None = Field("100m", description="CPU Quota (예: 100m)")
    memory: str | None = Field("32Mi", description="Memory Quota (예: 32Mi)")
    disk: str | None = Field("32Mi", description="Disk Quota (예: 32Mi)")


class ExternalPortCreate(BaseModel):
    service_id: str = Field(..., description="서비스 ID (소문자/숫자/하이픈)")
    service_name: str = Field(..., description="서비스 이름")
    target_deployment_name: Optional[str] = Field(..., description="타겟 디플로이먼트 이름")
    port: int = Field(..., description="외부 노출 포트")
    target_port: int = Field(..., description="내부 컨테이너 포트")
    protocol: Literal["TCP", "UDP", "SCTP"] = Field("TCP", description="프로토콜")
    service_type: Literal["ClusterIP", "NodePort", "LoadBalancer"] = Field(
        "ClusterIP", description="서비스 타입"
    )


class ExternalPortUpdate(BaseModel):
    service_id: str = Field(..., description="서비스 ID")
    service_name: str | None = Field(None, description="서비스 이름")
    target_deployment_name: str | None = Field(None, description="타겟 디플로이먼트 이름")
    target_port: int | None = Field(None, description="내부 컨테이너 포트")
    protocol: Literal["TCP", "UDP", "SCTP"] | None = Field(None, description="프로토콜")
    service_type: Literal["ClusterIP", "NodePort", "LoadBalancer"] | None = Field(
        None, description="서비스 타입"
    )


class ExternalResourceUpdate(BaseModel):
    cpu: str | None = Field(None, description="CPU Quota")
    memory: str | None = Field(None, description="Memory Quota")
    disk: str | None = Field(None, description="Disk Quota")