# AgentNews 面试讲解主线

这份文档解决一个问题：如果面试官让你“完整讲一下这个项目”，你应该按什么顺序讲，才不会讲散。

## 1. 先讲项目目标

不要一上来讲技术栈，先讲目标：

这个项目最初是一个新闻类前后端项目，后面我把它升级成了一个移动端新闻平台加新闻 Agent 系统。目标不是只做聊天，而是围绕新闻场景，把检索、时效性、来源约束、缓存优化和工作流可观测性做完整。

## 2. 再讲业务底座

先从传统工程讲起：

- 前端是 Vue 3 移动端新闻 App
- 后端是 FastAPI
- 主数据在 MySQL
- Redis 负责分类、列表、详情缓存、热榜、浏览量聚合和会话状态

这里要强调：

- 这不是“先做 Agent，再找场景”
- 而是“先有业务场景，再把 Agent 嵌进去”

## 3. 解释为什么不能只做模型直连

你可以这样说：

如果只是前端直连模型接口，会有几个问题：

- 没有安全边界
- 没有来源约束
- 没有检索能力
- 没有工作流和观测
- 不适合新闻这种强时效、强真实性场景

所以后面我把 AI 页逐步收口到后端，并演进成受控工作流。

## 4. 讲检索路线演进

这段是项目亮点，建议按阶段讲：

1. 先做本地 lexical baseline  
   用 `MySQL candidate set + 规则打分` 先打通 grounded QA 闭环。

2. 再接 Tavily web search  
   解决本地新闻库覆盖不全、无法回答最新问题的问题。

3. 再接 Qdrant 和本地 hybrid retrieval  
   用 `lexical + vector` 做本地混合召回，提升语义召回能力。

4. 最后做 planner 和 route-aware filtering  
   把问题分成 `local-first / hybrid / web-first`，不是所有问题都走同一条检索链路。

这一段建议明确说：

我不是一开始就上向量检索，而是先做可解释 baseline，再逐步升级到更适合新闻场景的 hybrid retrieval。

## 5. 讲 Agent 工作流

这里直接讲节点：

- query-analysis
- retrieval-planner
- retrieval
- route-filter
- final-rerank
- generator
- verifier
- response-formatter

然后说明：

- 前期先按 LangGraph 的思想做 stateful workflow
- 后面再迁移到真正的 `LangGraph StateGraph`
- 这样做的好处是工作流清晰、节点边界明确、LangSmith trace 也更自然

## 6. 讲记忆和会话窗口

这部分要分开说：

- `session memory`
  用 Redis 保存 recent messages 和 summary memory，解决会话上下文延续
- `session window management`
  把会话索引做成侧栏，支持切换、恢复和删除，体验上更接近主流聊天产品

要强调：

- 记忆不等于聊天窗口
- 记忆解决模型上下文
- 会话窗口解决用户操作体验

## 7. 讲幻觉控制

这一段面试官很爱问，建议分层说：

- grounded generation：回答必须绑定来源
- route-aware filtering：先把证据筛干净
- verifier：生成后再做规则校验
- low-confidence fallback：低置信度时保守回答
- no-evidence refusal：无证据时拒答

关键点：

我没有追求“永远给答案”，而是优先保证新闻回答可信。

## 8. 讲观测和评测

这一段把项目从 demo 拉到工程化：

- LangSmith：看 trace 和 run
- workflow graph export：看工作流图
- planner eval：评中间链路
- response eval：评最终回答质量
- failure case：沉淀失败样本，形成调优闭环

这里可以直接说：

项目后期不是继续堆功能，而是开始做观测、评测和反馈闭环。

## 9. 最后一段总结

推荐总结模板：

这个项目最大的价值不只是我做了一个新闻网站，而是我把新闻场景下的 Agent 关键问题都走了一遍：从缓存、检索、时效性，到工作流编排、幻觉控制、LangGraph、LangSmith 和评测闭环。整套方案不是一次性拍脑袋设计出来的，而是从轻量 baseline 逐步演进成现在这套可解释、可观测、可评测的新闻 Agent 架构。
