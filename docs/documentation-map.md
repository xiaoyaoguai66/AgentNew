# AgentNews 文档地图

这份文档只做一件事：告诉你不同文档应该在什么场景下看，避免后面复习时在大量文档里来回找。

## 1. 先看全局

- [README.md](D:/Code/Fastapi/AgentNews/README.md)
- [project-status-and-next-step.md](D:/Code/Fastapi/AgentNews/docs/project-status-and-next-step.md)
- [architecture-overview.md](D:/Code/Fastapi/AgentNews/docs/architecture-overview.md)
- [architecture-diagrams.md](D:/Code/Fastapi/AgentNews/docs/architecture-diagrams.md)

适合：

- 第一次快速了解项目
- 确认项目当前完成度
- 先建立整体架构视图

## 2. 简历与面试入口

- [resume-project-experience.md](D:/Code/Fastapi/AgentNews/docs/resume-project-experience.md)
- [interview-prep-index.md](D:/Code/Fastapi/AgentNews/docs/interview-prep-index.md)
- [interview-qa-cheatsheet.md](D:/Code/Fastapi/AgentNews/docs/interview-qa-cheatsheet.md)
- [interview-storyline.md](D:/Code/Fastapi/AgentNews/docs/interview-storyline.md)
- [demo-script.md](D:/Code/Fastapi/AgentNews/docs/demo-script.md)
- [github-showcase-guide.md](D:/Code/Fastapi/AgentNews/docs/github-showcase-guide.md)
- [langgraph-langsmith-interview-guide.md](D:/Code/Fastapi/AgentNews/docs/langgraph-langsmith-interview-guide.md)

适合：

- 写简历
- 面试前快速复习
- 准备项目讲解、答辩和演示

## 3. 核心方法演进

- [agent-method-evolution.md](D:/Code/Fastapi/AgentNews/docs/agent-method-evolution.md)

适合：

- 解释为什么先做 lexical baseline
- 解释为什么后续升级到 Qdrant / hybrid retrieval / Tavily
- 解释为什么采用受控工作流而不是一开始就做自由 Agent

## 4. 记忆与会话

- [m3-session-memory-and-summary.md](D:/Code/Fastapi/AgentNews/docs/m3-session-memory-and-summary.md)
- [m3-session-window-management.md](D:/Code/Fastapi/AgentNews/docs/m3-session-window-management.md)

适合：

- 讲清楚 session memory 的设计
- 讲清楚“记忆”和“聊天窗口管理”为什么是两层能力
- 解释为什么前端现在能像 ChatGPT 一样切换、恢复、删除会话

## 5. 检索、工作流与抗幻觉

- [m3-local-news-retrieval-grounding.md](D:/Code/Fastapi/AgentNews/docs/m3-local-news-retrieval-grounding.md)
- [m3-qdrant-local-vector-retrieval.md](D:/Code/Fastapi/AgentNews/docs/m3-qdrant-local-vector-retrieval.md)
- [m3-local-hybrid-retrieval.md](D:/Code/Fastapi/AgentNews/docs/m3-local-hybrid-retrieval.md)
- [m3-tavily-dual-retrieval.md](D:/Code/Fastapi/AgentNews/docs/m3-tavily-dual-retrieval.md)
- [m3-retrieval-planner.md](D:/Code/Fastapi/AgentNews/docs/m3-retrieval-planner.md)
- [m3-dual-route-filtering-rerank.md](D:/Code/Fastapi/AgentNews/docs/m3-dual-route-filtering-rerank.md)
- [m3-verifier-low-confidence-fallback.md](D:/Code/Fastapi/AgentNews/docs/m3-verifier-low-confidence-fallback.md)
- [m3-query-analysis-response-formatter.md](D:/Code/Fastapi/AgentNews/docs/m3-query-analysis-response-formatter.md)
- [m3-langgraph-stategraph-engine.md](D:/Code/Fastapi/AgentNews/docs/m3-langgraph-stategraph-engine.md)

适合：

- 讲检索路线
- 讲 Agent 工作流
- 讲为什么新闻场景需要 verifier 和 fallback

## 6. 观测、图与评测

- [m3-observability-langsmith-ready.md](D:/Code/Fastapi/AgentNews/docs/m3-observability-langsmith-ready.md)
- [m3-langsmith-sdk-tracing.md](D:/Code/Fastapi/AgentNews/docs/m3-langsmith-sdk-tracing.md)
- [m3-graph-export-evaluation-baseline.md](D:/Code/Fastapi/AgentNews/docs/m3-graph-export-evaluation-baseline.md)
- [m3-evaluation-feedback-loop.md](D:/Code/Fastapi/AgentNews/docs/m3-evaluation-feedback-loop.md)
- [m3-response-evaluator-casebook.md](D:/Code/Fastapi/AgentNews/docs/m3-response-evaluator-casebook.md)

适合：

- 讲 LangGraph 和 LangSmith 怎么分工
- 讲 trace、graph、eval 的区别
- 讲怎么做失败 case 沉淀和调优闭环

## 7. 前端产品化

- [m2-front-data-layer-and-home-hot-module.md](D:/Code/Fastapi/AgentNews/docs/m2-front-data-layer-and-home-hot-module.md)
- [m2-news-detail-experience-upgrade.md](D:/Code/Fastapi/AgentNews/docs/m2-news-detail-experience-upgrade.md)
- [m2-profile-favorite-history-unification.md](D:/Code/Fastapi/AgentNews/docs/m2-profile-favorite-history-unification.md)
- [m2-ai-assistant-interface-upgrade.md](D:/Code/Fastapi/AgentNews/docs/m2-ai-assistant-interface-upgrade.md)

适合：

- 讲移动端新闻 App 怎么从基础页面升级成产品化界面
- 讲新闻消费链路和 AI 助手链路如何融合

## 8. 交付、验证与上线准备

- [testing-checklist.md](D:/Code/Fastapi/AgentNews/docs/testing-checklist.md)
- [m4-automated-smoke-tests.md](D:/Code/Fastapi/AgentNews/docs/m4-automated-smoke-tests.md)
- [m4-integration-tests-and-final-showcase.md](D:/Code/Fastapi/AgentNews/docs/m4-integration-tests-and-final-showcase.md)
- [m4-dev-check-and-demo-materials.md](D:/Code/Fastapi/AgentNews/docs/m4-dev-check-and-demo-materials.md)
- [m4-ci-and-delivery-hardening.md](D:/Code/Fastapi/AgentNews/docs/m4-ci-and-delivery-hardening.md)
- [final-delivery-checklist.md](D:/Code/Fastapi/AgentNews/docs/final-delivery-checklist.md)

适合：

- 本地回归
- 演示前检查
- 上传 GitHub 前做最后交付核对
