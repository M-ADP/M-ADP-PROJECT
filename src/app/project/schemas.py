from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, constr

from src.core.client.application import ApplicationHealthStatus

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
        0.5,
        ge=0.5,
        le=1.0,
        description="GB 단위 (512MB ~ 1024MB, 기본 0.5GB)",
    )
    max_disk: float = Field(
        2.0,
        ge=2.0,
        le=50.0,
        description="GB 단위 (2GB ~ 50GB, 기본 2GB)",
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
        ge=0.5,
        le=1.0,
        description="GB 단위 (512MB ~ 1024MB)",
    )
    max_disk: float | None = Field(
        None,
        ge=2.0,
        le=50.0,
        description="GB 단위 (2GB ~ 50GB, 늘리기만 가능)",
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
        description="프로젝트 최대 메모리(GB)",
    )
    max_disk: float = Field(
        ...,
        description="프로젝트 최대 디스크(GB)",
    )


class ResourceMetricSnapshot(BaseModel):
    limit: str
    used: str
    percentage: float
    unit: str


class ResourceSnapshot(BaseModel):
    limit: int
    used: int
    percentage: float


class ProjectResourceSnapshot(BaseModel):
    project_id: str
    cpu: ResourceMetricSnapshot
    memory: ResourceMetricSnapshot
    disk: ResourceMetricSnapshot
    instance: ResourceSnapshot


class ApplicationItem(BaseModel):
    id: int
    name: str
    pod_count: int = Field(0, ge=0)
    exposed_port: int | None = None
    cpu_usage_percent: float | None = None
    ram_usage_percent: float | None = None
    health_status: ApplicationHealthStatus = "STOPPED"


class ProjectDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    my_role: Literal["OWNER", "MEMBER"] = Field(
        ...,
        description="현재 사용자의 프로젝트 내 역할",
    )
    deployments: list[ApplicationItem]
    resource: ProjectResourceSnapshot


# ===== Project Member Schemas =====


class ProjectMemberAdd(BaseModel):
    user_id: int = Field(
        ...,
        description="초대할 사용자의 ID",
        examples=["windeath44"],
    )


class ProjectMemberInvite(BaseModel):
    user_id: int = Field(
        ...,
        description="초대할 사용자의 ID",
        examples=[2],
    )


class ProjectMemberInvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="초대 식별자")
    project_id: int = Field(..., description="프로젝트 식별자")
    invitee_user_id: int = Field(..., description="초대 대상 사용자 식별자")
    invitee_email: str = Field(..., description="초대 대상 이메일 주소")
    status: Literal["PENDING", "ACCEPTED", "REJECTED", "CANCELED", "EXPIRED"] = Field(
        ...,
        description="초대 상태",
    )
    created_at: datetime = Field(..., description="초대 생성 일시")
    expires_at: datetime = Field(..., description="초대 만료 일시")
    responded_at: datetime | None = Field(None, description="초대 응답 일시")


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
