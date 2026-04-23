# AgentNews 演示脚本

这份脚本用于 5 到 8 分钟项目演示。目标不是把所有功能都点一遍，而是让面试官快速理解：这是一个新闻平台，也是一个具备检索、工作流、观测和评测能力的新闻 Agent。

## 1. 开场定位

一句话版本：

`AgentNews` 是一个移动端新闻平台，我在这个项目里把传统新闻业务链路和新闻 Agent 结合起来，重点解决了缓存、检索、时效性、幻觉控制和工作流可观测性问题。

## 2. 先演示新闻产品主链路

建议顺序：

1. 打开首页，展示分类切换、热门快读、新闻流
2. 点进详情页，展示正文阅读、阅读量、相关推荐
3. 进入“我的 / 收藏 / 历史”，说明前端已经产品化，不是只做了一个 AI 页面

这一段的目的：

- 证明项目不是“只有聊天框”
- 证明有真实业务场景和用户行为链路

## 3. 再演示 AI 助手

建议准备 3 类问题：

1. `根据本地新闻库总结一下科技热点`
   预期：`local-first`

2. `今天最新的卫星发射计划有什么进展`
   预期：`web-first`

3. `最近科技新闻里哪些变化最可能影响大模型行业`
   预期：`hybrid`

演示时重点看：

- `retrievalPlan`
- `plannerReason`
- `sources`
- `verificationStatus`
- `workflow trace`
- `session window`

这里可以顺手点开左上角“会话”，说明现在支持像主流聊天产品一样切换、恢复和删除历史会话。

## 4. 展示工作流图和 LangSmith

先展示：

- `GET /api/ai/workflow/graph`

说明：

- 当前主链路已经迁移到 `LangGraph StateGraph`
- 节点包括：
  `query-analysis -> retrieval-planner -> retrieval -> route-filter -> final-rerank -> generator -> verifier -> response-formatter`

再展示：

- LangSmith trace

说明：

- 项目保留了本地 `workflowTrace`
- 同时接入了 LangSmith 官方 tracing
- 所以既能本地调试，也能平台化看 trace

## 5. 展示评测与反馈闭环

展示：

- `GET /api/ai/eval/dataset`
- `POST /api/ai/eval/run`
- `POST /api/ai/eval/response/run`

说明：

- 项目不只追求“能回答”
- 还做了 planner eval 和 response-level eval
- 失败 case 会沉淀下来继续调 heuristic 和 guardrail

## 6. 最后一段总结

推荐收尾：

这个项目不是简单把大模型接到前端，而是先把新闻业务链路做稳，再围绕新闻场景把 Agent 的关键问题补齐。整个过程中，我重点做了三件事：一是用 Redis 把高频读写链路和会话状态做稳，二是把新闻检索从 lexical baseline 逐步升级到本地 hybrid retrieval 和 web search，三是把 Agent 做成可解释、可观测、可评测的工作流，而不是黑盒聊天。
