# LangGraph / LangSmith 面试理解指南

## 先给结论

### 你现在到底用的是 `LangGraph` 的思想还是语法

当前项目用的是：

- `LangGraph` 的思想
- `LangGraph-ready` 的结构

当前项目还没正式用的是：

- `langgraph` 官方包
- `StateGraph`
- `add_node`
- `add_edge`
- `compile`

所以最准确的说法不是：

> 我已经用了 LangGraph

而是：

> 我已经把 Agent 主链路重构成了 LangGraph 风格的 stateful workflow，但还没有正式迁移到 LangGraph 官方语法层。

### 你现在到底用的是 `LangSmith` 还是没有

当前项目是：

- `LangSmith-ready`

不是：

- 已经正式接通 `LangSmith tracing`

也就是说，你已经把官方观测平台需要的几个核心概念准备好了：

- trace
- run
- workflow trace
- local run log

但还没有真正把这些运行记录通过 LangSmith SDK 发到官方平台。

## 为什么要这样做，而不是一开始就直接用 LangGraph 语法

因为项目演进的关键不是“先把框架名用上”，而是先把工作流边界理顺。

如果一开始就直接写：

- `StateGraph`
- `add_node`
- `add_edge`

但内部其实还没有清晰的：

- state
- node input/output
- trace
- verifier / formatter 边界

那本质上只是“把一串函数硬包进图里”，并不会真正提升设计质量。

所以当前项目的顺序是：

1. 先把工作流节点拆出来
2. 先把统一状态和执行轨迹做出来
3. 再把观测和运行记录补上
4. 最后再迁移到 LangGraph 官方语法

这条顺序更工程化，也更适合面试解释。

## 当前项目逻辑全景

现在这条新闻 Agent 链路可以这样理解：

```text
用户问题
-> Query Analysis
-> Retrieval Planner
-> Local Retrieval
-> Web Search
-> Route-Aware Filtering
-> Final Rerank
-> Generator
-> Verifier
-> Response Formatter
-> 返回 answer / sources / confidence / trace
```

### 1. Query Analysis

先理解问题本身：

- 是事实问答还是总结
- 时效性要求高不高
- 更偏本地新闻还是更偏 Web

### 2. Retrieval Planner

把问题分成：

- `local-first`
- `hybrid`
- `web-first`

### 3. Local Retrieval

本地新闻现在不是单一路径，而是：

- lexical baseline
- Qdrant vector retrieval
- local hybrid retrieval

### 4. Web Search

接 Tavily 作为第二检索源。  
中文问题会先 query rewrite，再发 Web search。

### 5. Route-Aware Filtering

不是所有召回都直接保留。  
当前计划会影响：

- 本地结果保留量
- Web 结果保留量
- 不同来源的证据占比

### 6. Final Rerank

把本地与 Web 融合之后再排一次。  
当前是轻量工程型 rerank，不是大型 cross-encoder。

### 7. Generator

大模型只基于证据生成 grounded answer。

### 8. Verifier

判断：

- 是否证据不足
- 是否需要保守表达
- 是否应该拒答

### 9. Response Formatter

最后把输出整理成：

- answer
- sources
- confidence
- follow-up suggestions
- workflow trace

## 现在项目里哪些东西已经有了

### 已经有

- stateful workflow
- workflow trace
- retrieval planner
- local + web dual retrieval
- verifier
- formatter
- traceId / runId
- local run log

### 还没正式接入

- LangGraph 官方语法
- LangSmith 官方 tracing SDK
- LangSmith 平台里的 run/trace 可视化

## LangSmith 你后面怎么接最合理

你之前记得“要单独写一个 py 文件”，这个在工程上很常见。  
更准确地说，是通常会有一层独立的 tracing/setup 模块，负责：

1. 读取：
   - `LANGSMITH_TRACING`
   - `LANGSMITH_API_KEY`
   - `LANGSMITH_PROJECT`
2. 初始化官方 SDK tracing
3. 把每轮工作流运行送到 LangSmith

所以你后面完全可以这样做：

- 新增一个 `langsmith_tracing_service.py`
- 或者把这部分并进当前 `agent_observability_service.py`

关键不在“文件名”，而在“有没有把当前 workflow 的 run 真正接到官方平台”。

## 你后面在面试里怎么回答

### 问：你现在是 LangGraph 吗？

推荐回答：

> 严格说我现在是 LangGraph 思想和结构层，不是官方语法层。当前我已经把 Agent 链路拆成 stateful workflow，节点包括 query analysis、planner、retrieval、filter、rerank、generator、verifier 和 formatter，也记录了 workflow trace。所以它已经是 LangGraph-ready。后面如果要正式迁到 LangGraph，我主要是把这些节点和状态映射到 StateGraph，而不是从零重构。

### 问：为什么不一开始就直接用 LangGraph？

推荐回答：

> 因为我想先把工作流边界理清楚。很多项目一开始就直接套图框架，但内部 state 和 node boundary 不清楚，最后只是把一串函数包进 graph。我的做法是先让 state、node、trace 这三层稳定，再接官方图编排框架，这样迁移成本更低，也更符合工程演进顺序。

### 问：LangSmith 你接了吗？

推荐回答：

> 当前还没正式接 LangSmith 官方 tracing SDK，但已经做到了 LangSmith-ready。我已经给每轮问答生成了 traceId 和 runId，并把运行记录落到了本地 run log，还把 workflow trace 结构化返回给前端。后面接 LangSmith 时，只需要把现有 observability 层接到官方平台，而不是重新设计运行链路。

### 问：为什么先做本地 run log？

推荐回答：

> 因为我想先把观测模型跑通。先解决 trace、run、workflow trace、失败 case 记录这些底层问题，再接平台。这样后面无论是接 LangSmith 还是做离线评测，底层数据结构都已经准备好了。

## 现在这套项目你可以怎么概括

推荐一句话版本：

> 这是一个基于 FastAPI + Vue + MySQL + Redis + Qdrant 的移动端新闻平台，我把新闻 Agent 主链路逐步演进成了 LangGraph 风格的 stateful workflow，并补了本地 run trace 和 LangSmith-ready observability，为后续正式迁移到 LangGraph / LangSmith 留好了结构接口。
