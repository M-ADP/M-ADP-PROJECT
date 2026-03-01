from pydantic import BaseModel, ConfigDict, Field, constr, field_validator

from src.core.domain.dns import DNSState


class DNSCreate(BaseModel):
    subdomain: constr(strip_whitespace=True, min_length=1, max_length=63) = Field(
        ...,
        description="DNS 서브도메인 (mdeveloper.platform 앞에 붙을 이름)",
        examples=["my-app"],
    )

    @field_validator("subdomain")
    @classmethod
    def validate_subdomain(cls, v: str) -> str:
        # 서브도메인 유효성 검사: 영문자, 숫자, 하이픈만 허용
        if not all(c.isalnum() or c == "-" for c in v):
            raise ValueError("서브도메인은 영문자, 숫자, 하이픈만 사용할 수 있습니다.")
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("서브도메인은 하이픈으로 시작하거나 끝날 수 없습니다.")
        return v.lower()


class DNSResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    dns_name: str
    state: DNSState
    port_id: int | None = None


class DNSUpdate(BaseModel):
    subdomain: constr(strip_whitespace=True, min_length=1, max_length=63) = Field(
        ...,
        description="변경할 DNS 서브도메인",
        examples=["new-subdomain"],
    )

    @field_validator("subdomain")
    @classmethod
    def validate_subdomain(cls, v: str) -> str:
        if not all(c.isalnum() or c == "-" for c in v):
            raise ValueError("서브도메인은 영문자, 숫자, 하이픈만 사용할 수 있습니다.")
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("서브도메인은 하이픈으로 시작하거나 끝날 수 없습니다.")
        return v.lower()


class DNSPortBinding(BaseModel):
    port_id: int = Field(
        ...,
        description="바인딩할 공개 포트 ID",
        examples=[123456789],
    )
