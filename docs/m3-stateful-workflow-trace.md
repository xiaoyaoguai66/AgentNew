# M3.13 Stateful Workflow 与执行轨迹

## 这一阶段为什么要做

到 `M3.12` 为止，项目已经有一条比较完整的受控链路：

- Query Analysis
- Retrieval Planner
- Retrieval
- Route-Aware Filtering
- Final Rerank
- Generator
- Verifier
- Response Formatter

但这些节点虽然逻辑上已经存在，代码里还是“顺序调一串服务”。

这会有两个问题：

1. 后面如果接 `LangGraph`，还需要再重新梳理节点输入输出
2. 当前虽然知道系统“做了哪些事”，但用户和开发者还看不到一轮回答到底走了哪些节点、每步产出了什么

所以这一阶段补的是：

- `Stateful Workflow`
- `Workflow Trace`

目标是让系统从“有节点概念”升级成“有状态、有轨迹的节点工作流”。

---

## 这一阶段做了什么

### 1. 新增 Agent Workflow Service

新增：

- `backend/services/agent_workflow_service.py`

这层把当前主链路真正收口成一个状态化工作流。

当前流程变成：

```text
query-analysis
-> retrieval-planner
-> retrieval
-> route-filter
-> final-rerank
-> generator
-> verifier
-> response-formatter
```

每个节点执行时，都会把结果写回统一的 workflow state。

### 2. 新增 Workflow State

这一步新增了一个内部的 `WorkflowState`，统一保存：

- query analysis 结果
- retrieval planner 决策
- local / web sources
- merged sources
- confidence
- verification result
- follow-up suggestions
- workflow trace

这一步的价值很高，因为它意味着：

**系统不再只是“执行了一堆函数”，而是“围绕一份状态逐步推进”。**

### 3. 新增 Workflow Trace

后端现在会为每一轮对话记录执行轨迹，每个节点都会产出：

- `stepIndex`
- `node`
- `status`
- `detail`
- `durationMs`

也就是说，系统不只知道最后回答是什么，还能告诉你：

- 先做了问题分析
- 决定了哪种检索计划
- 检索到了多少本地和 Web 来源
- rerank 后保留了多少来源
- verifier 是正常通过还是触发了保护

### 4. 响应中新增 Workflow 信息

`AiChatResponse` 现在新增：

- `workflowSummary`
- `workflowTrace`

前端 AI 页也会显示：

- 顶部状态：`Workflow Stateful`
- 每条回答的工作流摘要
- 每个节点的执行轨迹

这一步让系统从“黑盒执行”变成“可观察工作流”。

---

## 技术名词解释

### 1. Stateful Workflow

`Stateful Workflow` 指的是：

**每个节点不是各算各的，而是围绕同一份状态逐步更新。**

这和简单的函数串行调用不一样。

函数串行调用通常是：

- 上一步返回什么，下步就接什么

而状态化工作流是：

- 整个流程围绕一份统一状态推进
- 每个节点修改或补充其中一部分

这更适合后面迁移到 `LangGraph` 这种图式编排框架。

### 2. Workflow Trace

`Workflow Trace` 指的是：

**把每个节点的执行轨迹显式记录下来。**

它的作用包括：

- 调试
- 演示
- 观测
- 面试讲解

当前 trace 里每一步都会带：

- 节点名
- 节点状态
- 节点说明
- 耗时

### 3. LangGraph-ready

这里说的 `LangGraph-ready`，不是已经正式接入了 LangGraph，而是：

**当前节点和状态已经按图编排思维拆好了。**

后面如果你接 LangGraph，主要做的是：

- 把当前节点注册成 graph node
- 把当前 state 迁成 graph state
- 把当前 trace 接入图级观测

而不是从零推翻重写。

---

## 为什么这一步重要

这一阶段对面试价值非常高，因为它把你的系统从：

```text
能回答问题
```

升级成了：

```text
有状态工作流
+ 有节点边界
+ 有执行轨迹
+ 可继续迁移到 LangGraph
```

这意味着你后面可以更自然地回答：

- 为什么适合迁到 LangGraph
- LangGraph 之前你做了哪些准备
- 你现在的工作流节点是什么
- 你如何观测每一轮 Agent 执行

---

## 怎么测试

### 1. 看状态接口

访问：

- `GET /api/ai/status`

新增字段预期：

- `workflowEnabled = true`
- `workflowStyle = stateful-node-pipeline`
- `workflowNodes` 包含 8 个节点

### 2. 看 AI 页顶部状态

打开 AI 页，顶部应新增：

- `Workflow Stateful`

### 3. 看每条回答的 Workflow Summary

问任意一个问题后，回答里应出现：

- `工作流：query-analysis -> retrieval-planner -> ...`

### 4. 看 Workflow Trace

每条回答下方应出现节点轨迹，例如：

- 问题分析
- 检索规划
- 检索执行
- 双路过滤
- 最终排序
- 回答生成
- 回答校验
- 输出整理

### 5. 看不同场景下的 trace 是否变化

例如：

- 无证据场景应更容易出现 verifier 的 `fallback`
- 低置信度场景 verifier 应是 `guarded`
- 正常场景 verifier 应是 `completed`

---

## 和后续 LangGraph / LangSmith 的关系

这一步之后，系统已经有了：

- state
- nodes
- trace

因此后面无论你是：

- 接 `LangGraph`
- 接 `LangSmith` 风格的 trace 观测
- 做离线评测集

都会比直接在一串函数调用上硬接更自然。

所以 `M3.13` 的意义不是“加了个 trace 面板”，而是：

**把当前 Agent 真正收口成了 LangGraph-ready 的状态化工作流。**
