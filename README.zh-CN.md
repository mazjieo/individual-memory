# individual-memory

[English](README.md) | [简体中文](README.zh-CN.md)

基于 mem0 构建的本地长期记忆服务，面向 AI Agent 使用。

默认运行方式以 MCP 为核心：

- PostgreSQL + pgvector 保存记忆。
- Ollama 提供 LLM 和 embedding 模型。
- mem0 负责记忆写入、搜索和删除。
- MCP 向代码 Agent 暴露记忆工具。
- FastAPI REST 接口作为可选调试入口。

## 前置条件

确认宿主机上的 Ollama 正在运行，并且默认模型已经存在：

```powershell
ollama list
```

默认模型：

- LLM: `qwen3.5:9b`
- Embedding: `nomic-embed-text`

## Docker

启动默认服务：

```powershell
docker compose up -d --build
```

默认服务：

- PostgreSQL: `localhost:5432`
- MCP Streamable HTTP: `http://127.0.0.1:8001/mcp`

MCP 容器通过 `http://host.docker.internal:11434` 访问宿主机上的 Ollama。

## 可选 REST API

REST API 默认不会启动。只有需要手动调试时再启用：

```powershell
docker compose --profile api up -d --build
```

REST API:

```text
http://127.0.0.1:8000
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

所有 REST 响应统一为：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

## MCP 工具

MCP server 暴露以下 tools：

- `remember`: 写入长期个人或项目记忆。
- `recall`: 用自然语言搜索记忆。
- `memory_context`: 为 LLM prompt 构造紧凑的记忆上下文。
- `list_memories`: 列出某个用户和可选项目下的记忆。
- `get_memory`: 按 id 查看单条记忆。
- `forget_memory`: 按 id 删除单条记忆。
- `forget_all_memories`: 删除某个用户的全部记忆。

## MCP 客户端配置

如果客户端支持 Streamable HTTP，使用：

```json
{
  "mcpServers": {
    "individual-memory": {
      "url": "http://127.0.0.1:8001/mcp"
    }
  }
}
```

如果客户端通过子进程启动 MCP server，使用 stdio：

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

## 本地 Python 环境

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

以 stdio 方式运行 MCP：

```powershell
.\.venv\Scripts\python.exe -m individual_memory.mcp_server
```

运行可选 REST API：

```powershell
.\.venv\Scripts\python.exe -m uvicorn individual_memory.api:app --reload --host 127.0.0.1 --port 8000
```

## 项目结构

```text
individual_memory/
  api.py        # 可选 FastAPI REST 路由
  config.py     # 环境变量和 mem0 配置
  mcp_server.py # MCP tools
  schemas.py    # REST 请求/响应模型
  service.py    # mem0 封装、去重、上下文构造
```

## Agent 使用建议

开始任务前，用当前任务和项目名调用 `memory_context`。

完成有意义的工作后，只用 `remember` 保存长期有效的信息：

- 用户偏好
- 项目决策
- 架构约束
- 调试经验
- 下一步决策

不要保存密钥、大段日志、临时命令输出，或者当前代码里显而易见的事实。
