# AgentNews 简历项目经历

## 1. 推荐写法

推荐用你给的第二版，也就是“标题 + 核心聚焦 + 技术栈 + 项目亮点 bullet”的写法。

原因很直接：

- 更像大厂简历常见风格，扫描成本低
- 亮点是一条一条落下来的，方便面试官追问
- 比一整段描述更容易体现技术决策和工程拆分
- 你的项目功能已经很多，bullet 写法更容易控住信息密度

## 2. 推荐最终版本

**项目名称：** `NewsCopilot：面向新闻场景的智能助手平台`  
**时间：** `2026.01 - 2026.03`  
**核心聚焦：** 围绕新闻场景构建前后端新闻平台 + 检索增强 Agent，重点解决新闻类 AI 应用中的检索、时效性、幻觉控制、缓存优化与可观测性。  
**技术栈：** `Vue 3`、`Vite`、`Vant`、`FastAPI`、`SQLAlchemy`、`MySQL`、`Redis`、`Qdrant`、`Tavily Web Search`、`LangGraph`、`LangSmith`

- 基于 `Vue 3 + FastAPI + MySQL + Redis` 构建移动端新闻平台，完成首页、详情、收藏、历史、热门快读与 AI 助手链路，形成“新闻消费 + 新闻问答”一体化体验。
- 基于 `LangGraph StateGraph` 设计新闻 Agent 工作流，串联 `Query Analysis`、`Retrieval Planner`、`Hybrid Retrieval`、`Route-Aware Filtering`、`Rerank`、`Verifier`、`Formatter` 等节点，支持多阶段推理、工具调用与状态化执行。
- 构建 `MySQL candidate set + lexical baseline + Qdrant 向量检索 + local hybrid retrieval + Tavily Web Search` 的多源检索体系，兼顾实体精确召回、语义召回与最新信息补充，提升新闻问答的相关性与时效性。
- 设计企业级 `Redis` 缓存与状态体系，覆盖分类、列表、详情、相关推荐、热榜、浏览量聚合及 AI `session memory` / 会话窗口索引，采用 `cache-aside`、`TTL jitter`、`增量聚合 + 定时回刷`、`summary memory` 等策略优化高频访问与多轮对话体验。
- 引入 `Verifier`、`low-confidence fallback`、`no-evidence refusal`、`LangSmith tracing`、`evaluation baseline` 与 `workflow graph export`，提升新闻 Agent 的抗幻觉能力、节点级可观测性与评测闭环能力。

## 3. 更保守的压缩版

如果你投递的岗位更偏后端 / Agent 开发，也可以压成下面这版：

**项目名称：** `NewsCopilot：面向新闻场景的智能助手平台`  
**核心聚焦：** 围绕新闻场景构建前后端新闻平台 + 检索增强 Agent，重点解决新闻类 AI 应用中的检索、时效性、幻觉控制、缓存优化与可观测性。  
**技术栈：** `Vue 3`、`FastAPI`、`MySQL`、`Redis`、`Qdrant`、`LangGraph`、`LangSmith`

- 基于 `LangGraph` 构建新闻 Agent 工作流，串联查询分析、检索规划、本地 / Web 双路检索、过滤重排、校验与答案生成等阶段，支持状态化执行与节点级 tracing。
- 构建 `lexical baseline + Qdrant 向量检索 + hybrid retrieval + Tavily Web Search` 的多源检索体系，提升新闻问答的语义召回能力与时效性。
- 设计 `Redis` 缓存与会话状态体系，覆盖新闻高频读缓存、热榜与浏览量聚合、会话记忆与会话窗口索引，优化访问性能和多轮对话体验。
- 引入 `Verifier`、低置信度回退与无证据拒答机制，并结合 `LangSmith` tracing 与评测闭环，降低幻觉风险并增强可观测性。

## 4. 面试时怎么解释你为什么这样写

推荐思路：

- 第一条写“平台和业务闭环”，证明你不是只做了一个聊天页
- 第二条写“工作流和 Agent 编排”，证明你理解 Agent 不是简单调模型
- 第三条写“检索体系”，证明你理解新闻场景对本地库、向量检索和 Web 搜索的组合需求
- 第四条写“Redis 和记忆/会话”，证明你有后端工程设计能力
- 第五条写“Verifier + LangSmith + Eval”，证明你考虑了抗幻觉、可观测性和调优闭环

## 5. 建议

如果你实际简历版面只允许放 4 条，我建议优先保留：

1. Agent 工作流
2. 多源检索体系
3. Redis 缓存与会话状态
4. Verifier + LangSmith + Eval

前端移动端新闻平台可以并入第一条或放到项目名称后的短描述里。
