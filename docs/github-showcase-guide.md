# AgentNews GitHub 展示指南

这份文档用于回答一个实际问题：项目功能很多，但 GitHub 首页只能承载有限信息，应该怎么摆，面试官才最容易看懂。

## 1. GitHub 首页最重要的目标

不要追求把所有细节都堆在 README 首页，而是优先做到三点：

1. 面试官 30 秒能看懂项目是什么
2. 面试官 2 分钟能看懂亮点在哪
3. 面试官愿意继续点进文档看细节

## 2. 首页结构建议

推荐顺序：

1. 项目一句话定位
2. 技术栈
3. 架构图
4. 核心亮点 bullet
5. 快速启动
6. 核心 API
7. 文档入口

现在项目的 [README.md](D:/Code/Fastapi/AgentNews/README.md) 已经基本按这个逻辑组织。

## 3. 首页亮点怎么写

不要写成“我做了很多功能”，而要写成“我解决了哪些关键问题”。

推荐表达重点：

- 新闻业务链路完整
- Redis 缓存与热榜/浏览量聚合
- 混合检索：lexical + vector + web
- LangGraph 工作流
- Verifier 与抗幻觉
- LangSmith tracing 与 eval 闭环

## 4. 最值得展示的页面

如果你后面要补截图或录屏，优先展示：

1. 首页：证明不是只有 AI 页面
2. 新闻详情页：证明有真实阅读链路
3. AI 页：证明有 Agent 能力
4. 会话侧栏：证明有主流聊天产品体验
5. LangSmith trace / workflow graph：证明有工程化观测能力

## 5. 最值得展示的接口

如果要放 API 示例，优先这几个：

- `GET /api/ai/status`
- `POST /api/ai/chat`
- `GET /api/ai/sessions`
- `GET /api/ai/workflow/graph`
- `POST /api/ai/eval/run`
- `POST /api/ai/eval/response/run`

## 6. 面试官最容易被什么吸引

这个项目真正有区分度的，不是“用了大模型”，而是：

- 你先有业务场景，再做 Agent
- 你不是一开始就堆向量库，而是从 baseline 演进
- 你考虑了缓存、时效性、幻觉控制、可观测性和评测闭环
- 你做了会话记忆和会话窗口管理，而不是只做一页聊天框

## 7. 建议

如果你后面还有时间，最值得补的 GitHub 展示材料是：

- 3 到 5 张项目截图
- 一段 1 分钟左右演示 GIF 或短视频
- 一张更正式的系统架构图
- 一页“从 baseline 到 hybrid retrieval”的演进图
