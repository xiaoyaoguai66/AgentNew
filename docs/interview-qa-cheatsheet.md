# AgentNews 面试问答速记

## 1. 这个项目是什么

这是一个面向新闻场景的移动端新闻平台和新闻 Agent 系统。前端负责新闻消费体验，后端负责业务 API、缓存、检索、工作流、观测和评测，Agent 层负责把新闻问答做成可解释、可控、可评测的链路。

## 2. 为什么先做 lexical retrieval

因为我想先把 grounded QA 闭环搭起来。lexical baseline 基于 MySQL 候选集和规则打分，可解释性强、依赖少、上线快，适合先验证来源约束和问答链路。

## 3. 后面是不是纯向量检索

不是。新闻场景更适合 hybrid retrieval，而不是纯向量检索。新闻问题既有语义召回需求，也有强实体词、时间过滤和分类过滤需求，所以最终结构是 lexical + vector + metadata filter + rerank。

## 4. 为什么接 Tavily

本地新闻库只能回答站内已有数据的问题，没法覆盖最新事件和外部信息。Tavily 作为第二检索源补足时效性，但不是单点依赖；如果 Web 搜索失败，系统仍然能降级回本地检索。

## 5. 为什么不是完全自由的 Agent

新闻问答最怕幻觉和不可解释。完全自由 Agent 看起来更聪明，但更难控制来源约束和失败模式。所以我选的是受控工作流：`Query Analysis -> Planner -> Retrieval -> Filter -> Rerank -> Verifier -> Formatter`。

## 6. 记忆是怎么做的

我没有直接做长期用户画像，而是先做了会话级短期记忆。具体是用 Redis 保存 `sessionId` 对应的 recent messages 和 summary memory，把最近几轮原始消息保留在窗口里，把更早对话压缩成摘要，再把摘要作为 prompt 的上下文补充。这样能支持刷新后的会话恢复，也能控制上下文长度，但不会让记忆替代检索证据。

## 7. 聊天窗口管理和记忆有什么区别

记忆解决的是“模型在同一个会话里还能记住什么”，聊天窗口管理解决的是“用户怎么切换、恢复和删除多个会话”。我把这两层拆开做：Redis 一层存单个 session 的 recent messages 和 summary，另一层存会话索引列表，前端像主流聊天产品一样提供侧栏会话窗口。这样模型侧上下文管理和用户侧产品体验都清楚，后续也方便继续演进到多用户隔离或数据库落盘。

## 8. 你这里用的是 LangGraph 的思想还是官方语法

前期先用的是 LangGraph 的思想：先把 state、node、trace 设计稳定。后期再迁移到官方 `StateGraph` 语法。这样不是为了上框架而上框架，而是先把节点边界和状态结构理顺，再接入官方 graph runtime。

## 9. LangSmith 起什么作用

LangSmith 主要负责 tracing 和 evaluation。LangGraph 负责工作流执行，LangSmith 负责观测和评测。这个项目里我保留了本地 trace/run log，同时接入了 LangSmith SDK tracing，方便本地调试和平台化观测。

## 10. 怎么控制幻觉

不是只靠 prompt。这里有三层：

1. 检索约束
2. 工作流约束
3. 生成后校验

也就是 Retrieval、Filter、Rerank、Verifier、Fallback、Refusal 一起控制。

## 11. Redis 在这个项目里做了什么

Redis 除了分类、列表、详情这些公共读缓存，还承担浏览量增量聚合、热榜 ZSet、会话记忆和降级容错。浏览量先在 Redis 累加，再定时回刷 MySQL，是因为它是高频写、弱一致字段。

## 12. 这个项目后面还能怎么继续做

可以继续补三类能力：

- 更完整的自动化测试和 CI
- 更系统的 response-level evaluator 和 casebook
- 更强的长期记忆、用户偏好和多工具协同
