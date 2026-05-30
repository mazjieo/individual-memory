from __future__ import annotations

from functools import cached_property
from typing import Any

from mem0 import Memory

from .config import Settings, settings


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def _memory_text(item: dict[str, Any]) -> str:
    return item.get("memory") or item.get("data") or item.get("payload", {}).get("data") or ""


class MemoryService:
    def __init__(self, app_settings: Settings = settings):
        self.settings = app_settings

    @cached_property
    def memory(self) -> Memory:
        return Memory.from_config(self.settings.mem0_config())

    def _user_id(self, user_id: str | None) -> str:
        return user_id or self.settings.default_user_id

    def _project(self, project: str | None) -> str:
        return project or self.settings.default_project

    def _filters(self, user_id: str | None, project: str | None = None) -> dict[str, Any]:
        filters: dict[str, Any] = {"user_id": self._user_id(user_id)}
        if project:
            filters["project"] = self._project(project)
        return filters

    def find_duplicate(self, content: str, user_id: str | None, project: str | None) -> dict[str, Any] | None:
        normalized_content = _normalize_text(content)
        search_result = self.memory.search(
            query=content,
            top_k=self.settings.duplicate_search_limit,
            filters=self._filters(user_id),
            threshold=0,
        )

        for item in search_result.get("results", []):
            if _normalize_text(_memory_text(item)) == normalized_content:
                item_metadata = item.get("metadata") or {}
                item_project = item_metadata.get("project") or item.get("project")
                if item_project in (None, self._project(project)):
                    return item
        return None

    def add(
        self,
        content: str,
        *,
        user_id: str | None = None,
        project: str | None = None,
        metadata: dict[str, Any] | None = None,
        infer: bool = False,
        dedupe: bool = True,
    ) -> dict[str, Any]:
        if dedupe:
            duplicate = self.find_duplicate(content, user_id, project)
            if duplicate:
                return {"status": "duplicate", "memory": duplicate}

        effective_project = self._project(project)
        effective_metadata = {"project": effective_project, "source": "api"}
        effective_metadata.update(metadata or {})

        result = self.memory.add(
            messages=[{"role": "user", "content": content}],
            user_id=self._user_id(user_id),
            metadata=effective_metadata,
            infer=infer,
        )
        return {"status": "added", **result}

    def search(
        self,
        query: str,
        *,
        user_id: str | None = None,
        project: str | None = None,
        limit: int = 5,
        threshold: float = 0.1,
        rerank: bool = False,
    ) -> dict[str, Any]:
        return self.memory.search(
            query=query,
            top_k=limit,
            filters=self._filters(user_id, project),
            threshold=threshold,
            rerank=rerank,
        )

    def list(self, *, user_id: str | None = None, project: str | None = None, limit: int = 20) -> dict[str, Any]:
        return self.memory.get_all(filters=self._filters(user_id, project), top_k=limit)

    def get(self, memory_id: str) -> dict[str, Any]:
        return self.memory.get(memory_id)

    def update(self, memory_id: str, data: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.memory.update(memory_id, data, metadata=metadata)

    def delete(self, memory_id: str) -> dict[str, Any]:
        return self.memory.delete(memory_id)

    def delete_all(self, *, user_id: str | None = None) -> dict[str, Any]:
        return self.memory.delete_all(user_id=self._user_id(user_id))

    def context(
        self,
        query: str,
        *,
        user_id: str | None = None,
        project: str | None = None,
        limit: int = 5,
        threshold: float = 0.1,
        rerank: bool = False,
        max_chars: int = 2000,
    ) -> dict[str, Any]:
        result = self.search(
            query,
            user_id=user_id,
            project=project,
            limit=limit,
            threshold=threshold,
            rerank=rerank,
        )
        lines: list[str] = []
        seen: set[str] = set()
        for item in result.get("results", []):
            text = _memory_text(item)
            normalized = _normalize_text(text)
            if text and normalized not in seen:
                seen.add(normalized)
                lines.append(f"- {text}")

        context = "\n".join(lines)
        if len(context) > max_chars:
            context = context[: max_chars - 3].rstrip() + "..."

        return {"context": context, "results": result.get("results", [])}


memory_service = MemoryService()
