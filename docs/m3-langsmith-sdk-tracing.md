# M3.15 正式接入 LangSmith SDK Tracing

## 这一步做了什么

这一阶段把项目从 `LangSmith-ready` 推进到了 **可选开启的 LangSmith 官方 SDK tracing**。

本次改动包括：

1. 安装 `langsmith` Python SDK
2. 在 `observability` 层集中管理 LangSmith 配置和客户端
3. 把现有 stateful workflow 的关键节点接入官方 tracing
4. 保留原有本地 `workflowTrace` 和 `run log`
5. 前端继续显示：
   - `Trace / Run`
   - `Observability`
   - `LangSmith`

也就是说，现在系统有两层观测：

- 项目自己的本地工作流轨迹
- LangSmith 官方平台 trace

## 为什么这样做

到上一阶段为止，项目已经有：

- state
- node
- workflow trace
- traceId / runId
- local run log

所以这时最合理的下一步，不是立刻迁移 `LangGraph` 语法，而是先把 **官方观测平台** 接上。

原因很直接：

1. 面试价值更高  
   你可以明确讲：
   - 本地 trace 怎么做
   - 官方 trace 怎么接
   - 为什么先本地、后平台

2. 对现有代码侵入更小  
   现在已经有清晰节点边界，给这些节点加 tracing 比改写成图框架更稳。

3. 更符合工程演进顺序  
   先让观测跑通，再继续做 LangGraph 语法迁移，风险更低。

## 关键技术含义

### `LangSmith SDK tracing`

这是官方 Python SDK 的 tracing 方式。  
不是你自己写一个日志文件，而是把运行数据通过官方 SDK 发到 LangSmith 平台。

### `traceable`

官方提供的装饰器。  
它可以给普通函数、异步函数、检索函数、生成函数打 trace。

在当前项目里，我把它用在了：

- `Query Analysis`
- `Retrieval Planner`
- `Local Retrieval`
- `Web Retrieval`
- `Route Filter`
- `Final Rerank`
- `Generator`
- `Verifier`
- `Response Formatter`
- 整个 `AgentNews Workflow`

### `tracing_context`

官方提供的上下文。  
它的作用是给一整轮调用设置统一的：

- project
- metadata
- tags
- client

我这里用它把整轮问答挂在一个统一的 workflow 上，再让各个子节点 trace 自动归到这条链路下面。

### `LangGraph-ready`

当前项目依然是：

- `LangGraph-ready`

不是：

- 已正式使用 `StateGraph/add_node/add_edge`

这一步接的是 LangSmith，不是 LangGraph 语法本身。

## 实现原理

### 1. observability 层统一管理 SDK

新增 / 重构：

- `backend/services/agent_observability_service.py`

它负责：

- 判断 SDK 是否安装
- 初始化 LangSmith client
- 同步环境变量：
  - `LANGSMITH_TRACING_V2`
  - `LANGSMITH_API_KEY`
  - `LANGSMITH_PROJECT`
  - `LANGSMITH_ENDPOINT`
- 提供统一的：
  - `langsmith_traceable(...)`
  - `langsmith_context(...)`
  - `build_langsmith_extra(...)`

这样业务层不直接散落着官方 SDK 调用。

### 2. workflow 层节点化接 tracing

`backend/services/agent_workflow_service.py` 现在不只是本地记录 `workflowTrace`，还把关键节点通过 `@traceable` 接到了 LangSmith。

所以现在一轮问答同时会产生两种轨迹：

- 本地返回给前端的 `workflowTrace`
- 官方平台里的 LangSmith trace tree

### 3. 本地 run log 仍然保留

即使 LangSmith 开启，本地仍保留：

- `backend/data/agent_runs/agent_runs.jsonl`

原因是：

- 本地调试依然方便
- 平台不可用时仍有降级记录
- 这更符合企业项目的“多层观测”思路

## 当前配置方式

`.env` 建议至少有：

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=你的_langsmith_key
LANGSMITH_PROJECT=agentnews-dev
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

### 当前逻辑

- 如果 `LANGSMITH_TRACING=false`
  - 只保留本地 run log
  - LangSmith 状态显示 `Ready` 或 `Off`

- 如果 `LANGSMITH_TRACING=true` 但没配 key
  - 不会崩
  - 仍走本地 run log

- 如果 `LANGSMITH_TRACING=true` 且配了 `LANGSMITH_API_KEY`
  - LangSmith tracing 正式生效

## 如何测试

### 1. 本地状态

访问：

- `GET /api/ai/status`

重点看：

- `langsmithReady`
- `langsmithTracing`
- `langsmithConfigured`
- `observabilityEnabled`

### 2. 本地 run log

发一轮 AI 对话后：

- `GET /api/ai/runs/recent`
- 查看 `backend/data/agent_runs/agent_runs.jsonl`

都应该能看到新记录。

### 3. LangSmith 平台

如果你已经在 `.env` 配好了：

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
```

重启后端，再发起一轮 AI 对话。

预期：

1. `GET /api/ai/status` 返回：
   - `langsmithConfigured = true`
2. LangSmith 官方平台里能看到：
   - `AgentNews Workflow`
   - 下面挂着各个子节点 trace

## 这一步之后你怎么讲

推荐说法：

> 我当前项目已经不是停留在 LangSmith-ready，而是补了官方 SDK tracing。具体做法不是把业务代码到处塞 tracing，而是先抽了一层 observability service，在里面统一管理 LangSmith client、traceable decorator 和 tracing context。然后把现有 stateful workflow 的关键节点接到 LangSmith，同时保留本地 workflow trace 和 run log 作为降级观测。

## 和 LangGraph 的关系

这一步仍然不是 LangGraph 语法迁移，而是为后续迁移做观测基础。

你现在最准确的表达是：

1. 已经按 LangGraph 思想做了 stateful workflow
2. 已经按 LangSmith 思想和 SDK 做了运行观测
3. 后续再决定是否把工作流本体迁移到 LangGraph 官方语法
