from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, constr


class PortCreate(BaseModel):
    target_deployment_name: constr(strip_whitespace=True, min_length=1) = Field(
        ...,
        description="연결할 앱(Deployment) 이름",
        examples=["my-app"],
    )
    port: int = Field(
        ...,
        ge=1,
        le=65535,
        description="외부 노출 포트",
        examples=[80],
    )
    target_port: int = Field(
        ...,
        ge=1,
        le=65535,
        description="컨테이너 내부 포트",
        examples=[8080],
    )
    protocol: Literal["TCP", "UDP", "SCTP"] = Field(
        "TCP",
        description="통신 프로토콜",
        examples=["TCP"],
    )
    service_type: Literal["ClusterIP", "NodePort", "LoadBalancer"] = Field(
        "ClusterIP",
        description="서비스 타입",
        examples=["ClusterIP"],
    )


class PortUpdate(PortCreate):
    pass


class PortResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    service_id: str
    service_name: str
    target_deployment_name: str
    port: int
    target_port: int
    protocol: str
    service_type: str