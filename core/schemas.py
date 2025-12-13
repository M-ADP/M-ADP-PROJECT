from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    message: str
    data: T


class ErrorResponse(BaseModel):
    message: str
