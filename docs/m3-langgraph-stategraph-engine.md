# M3.16 LangGraph StateGraph Engine

## 本次做了什么

这一阶段把新闻 Agent 从“LangGraph 思想层”推进到了“LangGraph 官方 `StateGraph` 语法层”。

在上一阶段，项目已经具备了这些结构：

- 统一 `WorkflowState`
- 明确节点边界
- `workflowTrace`
- LangSmith SDK tracing

但当时工作流本体仍然是自定义 Python 状态流，只是设计上参考了 LangGraph。

这一次新增了真正的 `StateGraph` 执行引擎，并通过 `AGENT_WORKFLOW_ENGINE` 切换主入口：

- `legacy`：保留原来的自定义状态流
- `langgraph`：启用官方 `StateGraph` 工作流

当前默认走 `langgraph`。

## 为什么要这么做

### 1. 之前只有 LangGraph 的思想，不是官方语法

之前的实现本质上是：

```text
state -> node -> trace
```

这已经很接近 LangGraph，但还不是官方 API。

面试里如果只说“我用了 LangGraph”，会有一个风险：

- 面试官继续追问 `StateGraph`、`add_node`、`add_edge`、`compile`
- 你会发现自己实际项目里并没有真正使用这些语法

所以这一阶段必须补齐。

### 2. LangSmith 图视图更依赖真正的 Graph 执行

你之前在 LangSmith 里看到的更多是 trace / run / span。

原因不是 LangSmith 不行，而是当时工作流执行方式还是自定义 Python 流程。  
LangSmith 能看到 tracing，但它拿到的不是一个真正由 `StateGraph` 驱动的 graph run。

这一次改成 `StateGraph` 后，链路会更接近官方文档里展示的图形化节点结构和节点执行视图。

### 3. 这一步能把“思想层”变成“语法层”

之前你可以说：

> 我按 LangGraph 的状态流思想设计了工作流。

现在你可以进一步说：

> 我先按 LangGraph 思想把 Agent 拆成 stateful workflow，后续再迁移到官方 `StateGraph` 语法，这样节点、状态、trace 的边界都更清楚，也更利于 LangSmith 观测。

这个说法会更完整，也更经得住深问。

## 这一阶段的实现原理

### 1. StateGraph 是什么

`StateGraph` 是 LangGraph 官方的图编排入口。  
你可以把它理解为：

- `state`：整条工作流共享的数据对象
- `node`：每个处理步骤
- `edge`：节点之间怎么流转
- `compile()`：把声明式图结构编译成可执行工作流

当前项目里的节点是：

- `query-analysis`
- `retrieval-planner`
- `retrieval`
- `route-filter`
- `final-rerank`
- `generator`
- `verifier`
- `response-formatter`
- `no-evidence-response`

### 2. 为什么有 `no-evidence-response`

这是一个显式分支节点。

如果 `final-rerank` 之后没有足够证据，就不进入生成节点，而是直接进入拒答节点。

这类节点设计很适合新闻 Agent，因为新闻问答非常强调：

- 有证据再回答
- 没证据就拒答
- 不靠模型硬编

### 3. 这次不是推翻旧逻辑，而是换执行内核

旧版本的业务能力没有被推翻：

- Query Analysis
- Retrieval Planner
- Local/Web Retrieval
- Route-Aware Filtering
- Final Rerank
- Verifier
- Formatter

都还在。

变化在于：

- 以前是手动串这些服务
- 现在是把这些服务映射成 `StateGraph` 节点

这也是为什么我一直坚持先做“状态化工作流”，再迁移到官方 LangGraph 语法。

## 当前你该怎么理解 LangGraph 和 LangSmith 的关系

### 1. LangGraph 负责执行结构

LangGraph 解决的是：

- 状态怎么流转
- 节点怎么拆
- 分支怎么跳
- 哪些节点是顺序，哪些是条件跳转

### 2. LangSmith 负责观测

LangSmith 解决的是：

- 每轮 run 的 trace
- 每个节点执行了什么
- 哪个节点慢
- 哪个节点失败
- prompt / retriever / verifier 的行为是否符合预期

所以最准确的关系是：

```text
LangGraph = workflow runtime
LangSmith = observability / tracing / evaluation
```

## 本次改动后的状态

当前项目里关于 Agent 工作流的说法应该更新为：

- 工作流执行：`LangGraph StateGraph`
- 可观测性：`LangSmith SDK tracing + 本地 run log`
- 项目形态：`LangGraph-ready` 已升级为 `LangGraph syntax active`

## 如何测试

### 1. 状态接口

访问：

- `GET /api/ai/status`

重点确认：

- `workflowEnabled = true`
- `workflowEngine = "langgraph"`
- `workflowStyle = "langgraph-stategraph"`
- `graphVisualizationReady = true`

### 2. 前端状态

打开 AI 页，顶部应看到：

- `Workflow LangGraph`
- `Graph Ready`
- `LangSmith Configured` 或 `Ready`

### 3. 真实问答

发起一轮 AI 问答后：

- 前端仍应显示 `workflowSummary`
- 每个节点 trace 仍应存在
- LangSmith 平台里应更容易看到 graph 视图和节点执行

### 4. 切换回旧引擎

如果你想验证引擎切换机制，可以在 `.env` 里改：

```env
AGENT_WORKFLOW_ENGINE=legacy
```

重启后端后再访问状态接口，应看到旧工作流模式。

## 面试怎么讲

推荐说法：

> 我一开始没有直接为了用框架而用 LangGraph，而是先把新闻 Agent 主链路重构成 stateful workflow，拆清楚 query analysis、planner、retrieval、filter、rerank、generator、verifier、formatter 这些节点。等状态边界和 trace 都稳定之后，再迁移到 LangGraph 官方 `StateGraph` 语法。这样 LangSmith 不仅能看 trace，也更容易展示图结构和节点执行情况。

## 官方资料

- [LangGraph 官方文档](https://docs.langchain.com/langgraph)
- [LangSmith: Trace with LangGraph](https://docs.langchain.com/langsmith/trace-with-langgraph)
