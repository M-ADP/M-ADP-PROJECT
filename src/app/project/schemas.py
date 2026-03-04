from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, constr

from src.app.port.schemas import PortResponse


class ProjectMemberRole(str):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class ProjectCreate(BaseModel):
    name: constr(strip_whitespace=True, min_length=1) = Field(
        ...,
        description="고유한 프로젝트 이름",
        examples=["my-project"],
    )
    max_cpu: float = Field(
        0.1,
        ge=0.1,
        le=4.0,
        description="vCPU 기준 (기본 0.1v)",
    )
    max_memory: float = Field(
        32.0,
        ge=32.0,
        le=4096.0,
        description="MB 단위 (기본 32MB)",
    )
    max_disk: float = Field(
        32.0,
        ge=32.0,
        le=51200.0,
        description="MB 단위 (기본 32MB)",
    )


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    max_cpu: float
    max_memory: float
    max_disk: float


class ProjectNameUpdate(BaseModel):
    name: constr(strip_whitespace=True, min_length=1) = Field(
        ...,
        description="변경할 프로젝트 이름",
        examples=["windeath44"],
    )

class ProjectResourceUpdate(BaseModel):
    max_cpu: float | None = Field(
        None,
        ge=0.1,
        le=4.0,
        description="vCPU 기준 (0.1v ~ 4v)",
    )
    max_memory: float | None = Field(
        None,
        ge=32.0,
        le=4096.0,
        description="MB 단위 (32MB ~ 4GB)",
    )
    max_disk: float | None = Field(
        None,
        ge=32.0,
        le=51200.0,
        description="MB 단위 (32MB ~ 50GB, 늘리기만 가능)",
    )


class ResourceUsage(BaseModel):
    cpu: float = 0.0
    memory: float = 0.0
    disk: float = 0.0
    network: float = 0.0
    traffic_per_hour: float = 0.0


class DeploymentSummary(BaseModel):
    running: int = Field(
        0,
        ge=0,
        description="Running 상태인 배포 개수",
    )
    warning: int = Field(
        0,
        ge=0,
        description="Warning 상태인 배포 개수",
    )


class DeploymentStatus(BaseModel):
    state: str = Field(
        ...,
        description="프로젝트 상태 (예: RUNNING, STOPPED)",
    )
    message: str = Field(
        ...,
        description="상태 메시지 텍스트",
    )


class ProjectListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    my_role: Literal["OWNER", "MEMBER"] = Field(
        ...,
        description="현재 사용자의 프로젝트 내 역할",
    )
    domain: str | None = Field(
        None,
        description="프로젝트 도메인 (있을 경우)",
    )
    deployment_summary: DeploymentSummary
    deployment_status: DeploymentStatus


class ProjectAvailableResponse(BaseModel):
    status: bool = Field(
        ...,
        description="요청 사용자의 프로젝트 접근 가능 여부",
    )


class ProjectOwnerResponse(BaseModel):
    status: bool = Field(
        ...,
        description="해당 사용자가 프로젝트 소유자(OWNER)인지 여부",
    )


class ProjectResourceLimitResponse(BaseModel):
    project_id: int = Field(
        ...,
        description="조회한 프로젝트 ID",
    )
    max_cpu: float = Field(
        ...,
        description="프로젝트 최대 vCPU",
    )
    max_memory: float = Field(
        ...,
        description="프로젝트 최대 메모리(MB)",
    )
    max_disk: float = Field(
        ...,
        description="프로젝트 최대 디스크(MB)",
    )


class MetricPoint(BaseModel):
    timestamp: str
    value: float


class ApplicationItem(BaseModel):
    id: int
    name: str
    runtime: str | None = None
    pod_count: int = Field(0, ge=0)
    exposed_port: int | None = None
    cpu_usage_percent: float | None = None
    ram_usage_percent: float | None = None
    health_status: Literal["Healthy", "Unhealthy", "Stopped"] = "Stopped"


class ProjectDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    my_role: Literal["OWNER", "MEMBER"] = Field(
        ...,
        description="현재 사용자의 프로젝트 내 역할",
    )
    deployments: list[ApplicationItem]
    cpu_usage: list[MetricPoint]
    memory_usage: list[MetricPoint]
    disk_usage: list[MetricPoint]
    network_usage: list[MetricPoint]
    traffic_per_hour: list[MetricPoint]
    ports: list[PortResponse]


# ===== Project Member Schemas =====


class ProjectMemberAdd(BaseModel):
    user_id: int = Field(
        ...,
        description="초대할 사용자의 ID",
        examples=["windeath44"],
    )


class ProjectOwnerTransfer(BaseModel):
    target_user_id: int = Field(
        ...,
        description="소유권을 이전할 대상 MEMBER 멤버의 ID",
        examples=["windeath44"],
    )


class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int = Field(..., description="멤버의 사용자 식별자")
    username: str = Field(..., description="멤버의 표시 이름")
    profile_image: str | None = Field(None, description="프로필 이미지 URL")
    role: Literal["OWNER", "MEMBER"] = Field(..., description="프로젝트 내 역할")
    joined_at: datetime = Field(..., description="프로젝트 참여 일시")
