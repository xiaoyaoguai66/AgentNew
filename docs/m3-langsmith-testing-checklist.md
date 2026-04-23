# M3.15 LangSmith SDK Tracing 测试清单

## 1. SDK 是否安装

确认后端虚拟环境已安装：

- `langsmith`

当前项目已写入：

- `backend/requirements.txt`

## 2. 环境变量

根目录 `.env` 建议至少配置：

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=你的_langsmith_key
LANGSMITH_PROJECT=agentnews-dev
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

如果暂时不想接官方平台，可以设：

```env
LANGSMITH_TRACING=false
```

## 3. 状态接口检查

访问：

- `GET /api/ai/status`

重点确认：

- `observabilityEnabled = true`
- `langsmithReady = true`
- `langsmithTracing = true/false`
- `langsmithConfigured = true/false`

### 预期

- 只装 SDK、没配 key：
  - `langsmithReady = true`
  - `langsmithConfigured = false`

- 配好 tracing 和 key：
  - `langsmithConfigured = true`

## 4. 本地运行记录检查

发起一轮 AI 对话后：

- `GET /api/ai/runs/recent`

预期返回最近运行记录，并包含：

- `traceId`
- `runId`
- `startedAt`
- `finishedAt`
- `status`

同时检查：

- `backend/data/agent_runs/agent_runs.jsonl`

应追加一条记录。

## 5. 前端页面检查

打开 AI 页，顶部应看到：

- `Observability Local`
- `LangSmith Ready` 或 `LangSmith Configured`

发起一轮对话后，回答区域应看到：

- `Trace ...`
- `Run ...`

## 6. LangSmith 平台检查

当前提是 `.env` 已配置：

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
```

重启后端，再发起一轮 AI 对话。

预期在 LangSmith 平台中能看到：

- `AgentNews Workflow`
- 子节点：
  - `Query Analysis`
  - `Retrieval Planner`
  - `Local News Retrieval`
  - `Tavily Web Retrieval`
  - `Route Filter`
  - `Final Rerank`
  - `LLM Generation`
  - `Answer Verifier`
  - `Response Formatter`

## 7. 降级检查

把 `.env` 改成：

```env
LANGSMITH_TRACING=false
```

重启后端后再次测试：

预期：

- AI 功能不受影响
- 本地 run log 仍然正常
- 只是 LangSmith 平台不再新增 trace
