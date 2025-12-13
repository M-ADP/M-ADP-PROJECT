from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, constr


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

    id: str
    user_id: str
    name: str
    dns_id: Optional[str]
    max_cpu: float
    max_memory: float
    max_disk: float
