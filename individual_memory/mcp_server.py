from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import settings
from .service import memory_service


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value in (None, "") else int(value)


mcp = FastMCP(
    settings.app_name,
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=_int_env("MCP_PORT", 8000),
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def remember(
    content: str,
    user_id: str | None = None,
    project: str | None = None,
    metadata: dict[str, Any] | None = None,
    infer: bool = False,
    dedupe: bool = True,
) -> dict[str, Any]:
    """Store a durable personal or project memory."""
    return memory_service.add(
        content,
        user_id=user_id,
        project=project,
        metadata=metadata,
        infer=infer,
        dedupe=dedupe,
    )


@mcp.tool()
def recall(
    query: str,
    user_id: str | None = None,
    project: str | None = None,
    limit: int = 5,
    threshold: float = 0.1,
    rerank: bool = False,
) -> dict[str, Any]:
    """Search memories by natural language."""
    return memory_service.search(
        query,
        user_id=user_id,
        project=project,
        limit=limit,
        threshold=threshold,
        rerank=rerank,
    )


@mcp.tool()
def memory_context(
    query: str,
    user_id: str | None = None,
    project: str | None = None,
    limit: int = 5,
    threshold: float = 0.1,
    rerank: bool = False,
    max_chars: int = 2000,
) -> dict[str, Any]:
    """Build a compact memory context block for an LLM prompt."""
    return memory_service.context(
        query,
        user_id=user_id,
        project=project,
        limit=limit,
        threshold=threshold,
        rerank=rerank,
        max_chars=max_chars,
    )


@mcp.tool()
def list_memories(
    user_id: str | None = None,
    project: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """List stored memories for a user and optional project."""
    return memory_service.list(user_id=user_id, project=project, limit=limit)


@mcp.tool()
def get_memory(memory_id: str) -> dict[str, Any]:
    """Get a memory by id."""
    return memory_service.get(memory_id)


@mcp.tool()
def forget_memory(memory_id: str) -> dict[str, Any]:
    """Delete a memory by id."""
    return memory_service.delete(memory_id)


@mcp.tool()
def forget_all_memories(user_id: str | None = None) -> dict[str, Any]:
    """Delete all memories for a user. Use carefully."""
    return memory_service.delete_all(user_id=user_id)


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http")
        return
    mcp.run()


if __name__ == "__main__":
    main()
