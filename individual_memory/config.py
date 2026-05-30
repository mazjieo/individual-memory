from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_dotenv(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value in (None, "") else int(value)


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    return default if value in (None, "") else float(value)


@dataclass(frozen=True)
class Settings:
    app_name: str
    default_user_id: str
    default_project: str

    ollama_base_url: str
    llm_provider: str
    llm_model: str
    llm_temperature: float

    embedder_provider: str
    embedder_model: str
    embedding_dims: int

    pg_host: str
    pg_port: int
    pg_user: str
    pg_password: str
    pg_dbname: str
    pg_collection_name: str

    duplicate_search_limit: int

    @classmethod
    def from_env(cls) -> "Settings":
        _load_dotenv()
        return cls(
            app_name=os.getenv("APP_NAME", "individual-memory"),
            default_user_id=os.getenv("MEMORY_USER_ID", "mazjieo"),
            default_project=os.getenv("MEMORY_PROJECT", "individual-memory"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            llm_provider=os.getenv("MEMORY_LLM_PROVIDER", "ollama"),
            llm_model=os.getenv("MEMORY_LLM_MODEL", "qwen3.5:9b"),
            llm_temperature=_float_env("MEMORY_LLM_TEMPERATURE", 0.1),
            embedder_provider=os.getenv("MEMORY_EMBEDDER_PROVIDER", "ollama"),
            embedder_model=os.getenv("MEMORY_EMBEDDER_MODEL", "nomic-embed-text"),
            embedding_dims=_int_env("MEMORY_EMBEDDING_DIMS", 768),
            pg_host=os.getenv("POSTGRES_HOST", "localhost"),
            pg_port=_int_env("POSTGRES_PORT", 5432),
            pg_user=os.getenv("POSTGRES_USER", "mem0"),
            pg_password=os.getenv("POSTGRES_PASSWORD", "mem0"),
            pg_dbname=os.getenv("POSTGRES_DB", "mem0"),
            pg_collection_name=os.getenv("MEMORY_COLLECTION", "coding_memory"),
            duplicate_search_limit=_int_env("MEMORY_DUPLICATE_SEARCH_LIMIT", 10),
        )

    def mem0_config(self) -> dict[str, Any]:
        return {
            "llm": {
                "provider": self.llm_provider,
                "config": {
                    "model": self.llm_model,
                    "ollama_base_url": self.ollama_base_url,
                    "temperature": self.llm_temperature,
                },
            },
            "embedder": {
                "provider": self.embedder_provider,
                "config": {
                    "model": self.embedder_model,
                    "ollama_base_url": self.ollama_base_url,
                },
            },
            "vector_store": {
                "provider": "pgvector",
                "config": {
                    "host": self.pg_host,
                    "port": self.pg_port,
                    "user": self.pg_user,
                    "password": self.pg_password,
                    "dbname": self.pg_dbname,
                    "collection_name": self.pg_collection_name,
                    "embedding_model_dims": self.embedding_dims,
                },
            },
        }


settings = Settings.from_env()
