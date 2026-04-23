# AgentNews 面试准备索引

这份索引解决一个问题：文档很多，但面试前不可能全部重读。这里按“先讲清项目，再讲清方法，最后讲清细节”的顺序组织。

## 1. 先看这几份

- [resume-project-experience.md](D:/Code/Fastapi/AgentNews/docs/resume-project-experience.md)
- [architecture-overview.md](D:/Code/Fastapi/AgentNews/docs/architecture-overview.md)
- [architecture-diagrams.md](D:/Code/Fastapi/AgentNews/docs/architecture-diagrams.md)
- [project-status-and-next-step.md](D:/Code/Fastapi/AgentNews/docs/project-status-and-next-step.md)
- [interview-storyline.md](D:/Code/Fastapi/AgentNews/docs/interview-storyline.md)
- [demo-script.md](D:/Code/Fastapi/AgentNews/docs/demo-script.md)
- [github-showcase-guide.md](D:/Code/Fastapi/AgentNews/docs/github-showcase-guide.md)

这几份解决的是：

- 简历上怎么写
- 整体架构怎么讲
- 项目已经做到什么程度
- 面试时怎么完整讲一遍

## 2. 高频追问怎么准备

### 为什么 Redis 这样设计

- [m1-news-read-cache.md](D:/Code/Fastapi/AgentNews/docs/m1-news-read-cache.md)
- [m1-view-flush-and-hot-ranking.md](D:/Code/Fastapi/AgentNews/docs/m1-view-flush-and-hot-ranking.md)

### 为什么先 lexical，再做向量检索和 hybrid retrieval

- [agent-method-evolution.md](D:/Code/Fastapi/AgentNews/docs/agent-method-evolution.md)
- [m3-local-news-retrieval-grounding.md](D:/Code/Fastapi/AgentNews/docs/m3-local-news-retrieval-grounding.md)
- [m3-local-hybrid-retrieval.md](D:/Code/Fastapi/AgentNews/docs/m3-local-hybrid-retrieval.md)
- [m3-qdrant-local-vector-retrieval.md](D:/Code/Fastapi/AgentNews/docs/m3-qdrant-local-vector-retrieval.md)

### 为什么要接 Tavily，而不是只用本地库

- [m3-tavily-dual-retrieval.md](D:/Code/Fastapi/AgentNews/docs/m3-tavily-dual-retrieval.md)
- [m3-web-query-rewrite.md](D:/Code/Fastapi/AgentNews/docs/m3-web-query-rewrite.md)
- [m3-dual-route-filtering-rerank.md](D:/Code/Fastapi/AgentNews/docs/m3-dual-route-filtering-rerank.md)

### 为什么不是自由 Agent，而是受控工作流

- [m3-retrieval-planner.md](D:/Code/Fastapi/AgentNews/docs/m3-retrieval-planner.md)
- [m3-query-analysis-response-formatter.md](D:/Code/Fastapi/AgentNews/docs/m3-query-analysis-response-formatter.md)
- [m3-langgraph-stategraph-engine.md](D:/Code/Fastapi/AgentNews/docs/m3-langgraph-stategraph-engine.md)

### 记忆能力和会话窗口怎么讲

- [m3-session-memory-and-summary.md](D:/Code/Fastapi/AgentNews/docs/m3-session-memory-and-summary.md)
- [m3-session-window-management.md](D:/Code/Fastapi/AgentNews/docs/m3-session-window-management.md)

### 幻觉控制怎么讲

- [m3-verifier-low-confidence-fallback.md](D:/Code/Fastapi/AgentNews/docs/m3-verifier-low-confidence-fallback.md)
- [m3-response-evaluator-casebook.md](D:/Code/Fastapi/AgentNews/docs/m3-response-evaluator-casebook.md)

### LangGraph 和 LangSmith 到底怎么分工

- [langgraph-langsmith-interview-guide.md](D:/Code/Fastapi/AgentNews/docs/langgraph-langsmith-interview-guide.md)
- [m3-observability-langsmith-ready.md](D:/Code/Fastapi/AgentNews/docs/m3-observability-langsmith-ready.md)
- [m3-langsmith-sdk-tracing.md](D:/Code/Fastapi/AgentNews/docs/m3-langsmith-sdk-tracing.md)
- [m3-graph-export-evaluation-baseline.md](D:/Code/Fastapi/AgentNews/docs/m3-graph-export-evaluation-baseline.md)

## 3. 如果面试官继续深挖

### 评测和调优闭环

- [m3-evaluation-feedback-loop.md](D:/Code/Fastapi/AgentNews/docs/m3-evaluation-feedback-loop.md)
- [m3-response-evaluator-casebook.md](D:/Code/Fastapi/AgentNews/docs/m3-response-evaluator-casebook.md)

### 前端产品化

- [m2-front-data-layer-and-home-hot-module.md](D:/Code/Fastapi/AgentNews/docs/m2-front-data-layer-and-home-hot-module.md)
- [m2-news-detail-experience-upgrade.md](D:/Code/Fastapi/AgentNews/docs/m2-news-detail-experience-upgrade.md)
- [m2-profile-favorite-history-unification.md](D:/Code/Fastapi/AgentNews/docs/m2-profile-favorite-history-unification.md)
- [m2-ai-assistant-interface-upgrade.md](D:/Code/Fastapi/AgentNews/docs/m2-ai-assistant-interface-upgrade.md)

### 工程交付和可运行性

- [m4-automated-smoke-tests.md](D:/Code/Fastapi/AgentNews/docs/m4-automated-smoke-tests.md)
- [m4-integration-tests-and-final-showcase.md](D:/Code/Fastapi/AgentNews/docs/m4-integration-tests-and-final-showcase.md)
- [m4-dev-check-and-demo-materials.md](D:/Code/Fastapi/AgentNews/docs/m4-dev-check-and-demo-materials.md)
- [m4-ci-and-delivery-hardening.md](D:/Code/Fastapi/AgentNews/docs/m4-ci-and-delivery-hardening.md)

## 4. 最后回到测试

- [testing-checklist.md](D:/Code/Fastapi/AgentNews/docs/testing-checklist.md)
- [final-delivery-checklist.md](D:/Code/Fastapi/AgentNews/docs/final-delivery-checklist.md)

这两份最适合在演示前和提交前做最后复查。
