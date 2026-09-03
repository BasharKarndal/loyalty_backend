from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):

    success: bool

    message: str
    status_code: int

    data: T | None = None

    errors: list | None = None


    
  