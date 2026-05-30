from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Any = None


class MemoryAddRequest(BaseModel):
    content: str = Field(..., min_length=1)
    user_id: str | None = None
    project: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    infer: bool = False
    dedupe: bool = True


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    user_id: str | None = None
    project: str | None = None
    limit: int = Field(default=5, ge=1, le=50)
    threshold: float = Field(default=0.1, ge=0)
    rerank: bool = False


class MemoryContextRequest(MemorySearchRequest):
    max_chars: int = Field(default=2000, ge=100, le=12000)


class MemoryUpdateRequest(BaseModel):
    data: str = Field(..., min_length=1)
    metadata: dict[str, Any] | None = None
