from pydantic import BaseModel, Field


class ExternalProjectCreate(BaseModel):
    id: str = Field(..., description="프로젝트 ID")
    name: str = Field(..., description="프로젝트 이름")
    cpu: str | None = Field("100m", description="CPU Quota (예: 100m)")
    memory: str | None = Field("32Mi", description="Memory Quota (예: 32Mi)")
    disk: str | None = Field("32Mi", description="Disk Quota (예: 32Mi)")


class ExternalResourceUpdate(BaseModel):
    cpu: str | None = Field(None, description="CPU Quota")
    memory: str | None = Field(None, description="Memory Quota")
    disk: str | None = Field(None, description="Disk Quota")


