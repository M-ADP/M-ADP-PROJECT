from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, constr


class PortCreate(BaseModel):
    from_ip: constr(strip_whitespace=True, min_length=1) = Field(
        ...,
        description="허용할 출발지 IP 또는 CIDR",
        examples=["0.0.0.0/0", "10.0.0.1"],
    )
    from_port: int = Field(
        ...,
        ge=1,
        le=65535,
        description="공개할 포트 번호",
        examples=[80, 443],
    )
    port_number: int = Field(
        ...,
        ge=0,
        le=255,
        description="IANA protocol number",
        examples=[6, 17],
    )
    protocol: Literal["tcp", "udp", "icmp"] = Field(
        ...,
        description="통신 프로토콜",
        examples=["tcp"],
    )


class PortResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    from_ip: str
    from_port: int
    prot_number: int
    protocol: str
