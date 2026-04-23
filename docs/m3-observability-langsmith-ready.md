# M3.14 观测层与 LangSmith-Ready 设计

## 这一步做了什么

这一阶段没有继续改检索和回答策略，而是补了 Agent 的观测层：

1. 给每轮 AI 对话生成 `traceId` 和 `runId`
2. 把运行结果落到本地 `jsonl` run log
3. 在 `/api/ai/status` 里暴露 `Observability / LangSmith` 状态
4. 新增 `GET /api/ai/runs/recent` 调试接口
5. 前端 AI 页显示：
   - `Observability`
   - `LangSmith`
   - 每轮回答的 `Trace / Run`

## 为什么这样做

到 `M3.13` 为止，系统已经有：

- `state`
- `node`
- `trace`

这已经很接近 `LangGraph / LangSmith` 的工作方式了，但还差一层工程闭环：

- 每次运行有没有唯一 ID
- 每次运行有没有持久化记录
- 出错时有没有留下失败轨迹
- 后面如果接官方平台，要往哪里对接

所以这一步先做“本地版 LangSmith”：

- 先把 `trace/run` 概念跑通
- 先把本地记录能力做出来
- 后面再把这些运行数据接到官方 LangSmith

这样做的好处是，后面不是“从零开始接平台”，而是“把现有观测数据升级到官方观测平台”。

## 关键技术含义

### `traceId`

一次完整工作流链路的标识。  
你可以把它理解成“这一轮问答的总追踪号”。

### `runId`

一次具体运行实例的标识。  
在当前项目里，它和一次问答基本一一对应。

### `run log`

本地运行日志。  
当前保存在：

- `backend/data/agent_runs/agent_runs.jsonl`

每一行就是一条 JSON 运行记录，适合本地开发和调试。

### `LangSmith-ready`

意思不是“已经接了官方 LangSmith SDK”，而是：

- 工作流已经有节点
- 已经有统一状态
- 已经有 trace
- 已经有 run log
- 已经有 LangSmith 相关配置位

也就是只差最后一步官方 SDK / 平台接线，而不是概念和结构都还没准备好。

## 你现在到底是在用 LangGraph 的思想还是语法

当前项目是：

- **LangGraph 的思想和架构**

不是：

- **LangGraph 官方 Python 语法**

更准确地说：

1. 你现在已经在用 `stateful workflow / node pipeline / trace` 这一套 LangGraph 思想
2. 但代码里还没有真正引入 `langgraph` 包，也没有用官方的 `StateGraph`、`add_node`、`add_edge`

所以面试时最准确的说法是：

> 当前项目已经按 LangGraph 的状态流和节点编排思路重构成了 stateful workflow，并记录了 workflow trace；但还没有正式迁移到 LangGraph 官方语法层，属于 LangGraph-ready 而不是 LangGraph-SDK-native。

## LangSmith 现在是什么状态

当前项目是：

- **LangSmith-ready**

不是：

- **已经正式接入 LangSmith 官方 tracing**

你之前记得“LangSmith 要单独写一个 py 文件，把 API 配到官网去测”，这个理解有一半是对的：

1. LangSmith 通常确实需要单独配置：
   - `LANGSMITH_TRACING`
   - `LANGSMITH_API_KEY`
   - `LANGSMITH_PROJECT`
2. 很多项目也确实会单独写一个 tracing/setup 模块
3. 但不是“必须单独写一个 py 文件”这个形式才算接入

本质上需要的是：

- SDK tracing 打开
- API Key 可用
- 运行链路被官方 trace 到平台

官方文档可以参考：

- [LangGraph 官方文档](https://docs.langchain.com/langgraph)
- [LangSmith: Trace with LangGraph](https://docs.langchain.com/langsmith/trace-with-langgraph)

## 当前实现原理

### 后端

新增 `agent_observability_service.py`，负责：

- 创建 `traceId / runId`
- 记录成功运行
- 记录失败运行
- 读取最近运行记录
- 暴露 LangSmith-ready 状态

`agent_workflow_service.py` 现在会：

1. 进入工作流前先创建 `run_context`
2. 运行成功后记录完整 response
3. 运行失败后记录部分 trace 和 error
4. 把 `traceId / runId` 直接返回给前端

### 前端

AI 页会显示：

- `Observability Local`
- `LangSmith Ready / Configured`
- 每条回答的 `Trace / Run`

这意味着你在演示时可以直接指着页面讲：

- 这是这轮问答的 trace id
- 这是这轮运行的 run id
- 这是当前工作流轨迹
- 这是本地 run log / 后续 LangSmith 的接入位

## 环境变量

新增这些配置：

```env
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=agentnews-dev
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
AGENT_RUN_LOG_PATH=backend/data/agent_runs/agent_runs.jsonl
```

### 当前建议

如果你还没正式接 LangSmith：

- `LANGSMITH_TRACING=false`
- 先用本地 run log

如果后面要正式接 LangSmith：

- `LANGSMITH_TRACING=true`
- 配上 `LANGSMITH_API_KEY`
- 配好 `LANGSMITH_PROJECT`

## 如何测试

1. 重启后端
2. 访问：
   - `GET /api/ai/status`
3. 重点确认：
   - `observabilityEnabled = true`
   - `observabilityMode = local-trace-log`
   - `langsmithReady = true`
4. 发起一轮 AI 对话
5. 在返回中确认：
   - `traceId`
   - `runId`
6. 访问：
   - `GET /api/ai/runs/recent`
7. 预期能看到最近运行记录
8. 打开本地文件：
   - `backend/data/agent_runs/agent_runs.jsonl`
   也应该能看到对应记录

## 面试时怎么讲

推荐说法：

> 我当前项目已经按 LangGraph 的状态流和节点编排思路搭成了 stateful workflow，并把 query analysis、planner、retrieval、filter、rerank、generator、verifier、formatter 都拆成了显式节点。同时，我没有一开始就硬接 LangSmith，而是先做了本地 traceId、runId 和 run log，把观测链路跑通。这样后面接 LangSmith 时，不是重新设计工作流，而是把现有 trace/run 数据接到官方平台。
