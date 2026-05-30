# individual-memory

Local long-term memory service for AI agents, built on top of mem0.

The default runtime is MCP-first:

- PostgreSQL + pgvector stores memories.
- Ollama provides the LLM and embedding models.
- mem0 handles memory add/search/delete behavior.
- MCP exposes memory tools for coding agents.
- FastAPI REST endpoints are available as an optional debugging profile.

## Prerequisites

Make sure Ollama is running on the host and the default models are available:

```powershell
ollama list
```

Default models:

- LLM: `qwen3.5:9b`
- Embedding: `nomic-embed-text`

## Docker

Start the default stack:

```powershell
docker compose up -d --build
```

Default services:

- PostgreSQL: `localhost:5432`
- MCP Streamable HTTP: `http://127.0.0.1:8001/mcp`

The MCP container uses `http://host.docker.internal:11434` to access Ollama on the host.

## Optional REST API

The REST API is not started by default. Enable it only when you want a manual debugging endpoint:

```powershell
docker compose --profile api up -d --build
```

REST API:

```text
http://127.0.0.1:8000
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

All REST responses use:

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

## MCP Tools

The MCP server exposes:

- `remember`: store a durable personal or project memory.
- `recall`: search memories by natural language.
- `memory_context`: build a compact memory context block for an LLM prompt.
- `list_memories`: list stored memories for a user and optional project.
- `get_memory`: get a memory by id.
- `forget_memory`: delete a memory by id.
- `forget_all_memories`: delete all memories for a user.

## MCP Client Configuration

Use Streamable HTTP when your client supports it:

```json
{
  "mcpServers": {
    "individual-memory": {
      "url": "http://127.0.0.1:8001/mcp"
    }
  }
}
```

Use stdio when your client launches MCP servers as subprocesses:

```json
{
  "mcpServers": {
    "individual-memory": {
      "command": "D:\\code\\individual-memory\\.venv\\Scripts\\python.exe",
      "args": ["-m", "individual_memory.mcp_server"],
      "cwd": "D:\\code\\individual-memory",
      "env": {
        "POSTGRES_HOST": "localhost",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "MEMORY_USER_ID": "mazjieo",
        "MEMORY_PROJECT": "individual-memory"
      }
    }
  }
}
```

## Local Python Setup

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run MCP over stdio:

```powershell
.\.venv\Scripts\python.exe -m individual_memory.mcp_server
```

Run the optional REST API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn individual_memory.api:app --reload --host 127.0.0.1 --port 8000
```

## Project Structure

```text
individual_memory/
  api.py        # Optional FastAPI REST routes
  config.py     # Environment and mem0 config
  mcp_server.py # MCP tools
  schemas.py    # REST request/response models
  service.py    # mem0 wrapper, duplicate guard, context builder
```

## Agent Usage Guidance

At the start of a task, call `memory_context` with the current task and project name.

After meaningful work, call `remember` only for durable facts:

- user preferences
- project decisions
- architecture constraints
- debugging lessons
- next-step decisions

Do not store secrets, large logs, transient command output, or facts that are obvious from the current code.
