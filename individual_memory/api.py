from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config import settings
from .schemas import ApiResponse, MemoryAddRequest, MemoryContextRequest, MemorySearchRequest, MemoryUpdateRequest
from .service import MemoryService, memory_service


app = FastAPI(title=settings.app_name)


def ok(data: Any = None, message: str = "ok") -> dict[str, Any]:
    return ApiResponse(code=0, message=message, data=data).model_dump()


def get_service() -> MemoryService:
    return memory_service


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content=ApiResponse(code=500, message=str(exc), data=None).model_dump())


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict) and {"code", "message", "data"} <= set(detail):
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(code=exc.status_code, message=str(detail), data=None).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ApiResponse(code=422, message="validation error", data=exc.errors()).model_dump(),
    )


@app.get("/health")
def health() -> dict[str, Any]:
    return ok(
        {
            "app": settings.app_name,
            "collection": settings.pg_collection_name,
            "llm_model": settings.llm_model,
            "embedder_model": settings.embedder_model,
        }
    )


@app.post("/memories")
def add_memory(payload: MemoryAddRequest, service: MemoryService = Depends(get_service)) -> dict[str, Any]:
    result = service.add(
        payload.content,
        user_id=payload.user_id,
        project=payload.project,
        metadata=payload.metadata,
        infer=payload.infer,
        dedupe=payload.dedupe,
    )
    return ok(result)


@app.get("/memories")
def list_memories(
    user_id: str | None = None,
    project: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    service: MemoryService = Depends(get_service),
) -> dict[str, Any]:
    return ok(service.list(user_id=user_id, project=project, limit=limit))


@app.delete("/memories")
def delete_user_memories(user_id: str | None = None, service: MemoryService = Depends(get_service)) -> dict[str, Any]:
    return ok(service.delete_all(user_id=user_id))


@app.post("/memories/search")
def search_memories(payload: MemorySearchRequest, service: MemoryService = Depends(get_service)) -> dict[str, Any]:
    return ok(
        service.search(
            payload.query,
            user_id=payload.user_id,
            project=payload.project,
            limit=payload.limit,
            threshold=payload.threshold,
            rerank=payload.rerank,
        )
    )


@app.post("/context")
def build_context(payload: MemoryContextRequest, service: MemoryService = Depends(get_service)) -> dict[str, Any]:
    return ok(
        service.context(
            payload.query,
            user_id=payload.user_id,
            project=payload.project,
            limit=payload.limit,
            threshold=payload.threshold,
            rerank=payload.rerank,
            max_chars=payload.max_chars,
        )
    )


@app.get("/memories/{memory_id}")
def get_memory(memory_id: str, service: MemoryService = Depends(get_service)) -> dict[str, Any]:
    return ok(service.get(memory_id))


@app.patch("/memories/{memory_id}")
def update_memory(
    memory_id: str,
    payload: MemoryUpdateRequest,
    service: MemoryService = Depends(get_service),
) -> dict[str, Any]:
    return ok(service.update(memory_id, payload.data, metadata=payload.metadata))


@app.delete("/memories/{memory_id}")
def delete_memory(memory_id: str, service: MemoryService = Depends(get_service)) -> dict[str, Any]:
    return ok(service.delete(memory_id))
