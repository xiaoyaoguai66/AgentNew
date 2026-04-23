# M4 接口级集成测试与最终展示材料

## 1. 这一轮做了什么

这一轮补的是两类收尾能力：

- 接口级 integration test
- GitHub / 面试展示材料定稿

新增与更新位置：

- [backend/tests/integration_api.py](D:/Code/Fastapi/AgentNews/backend/tests/integration_api.py)
- [scripts/dev-check.ps1](D:/Code/Fastapi/AgentNews/scripts/dev-check.ps1)
- [.github/workflows/ci.yml](D:/Code/Fastapi/AgentNews/.github/workflows/ci.yml)
- [demo-script.md](D:/Code/Fastapi/AgentNews/docs/demo-script.md)
- [interview-storyline.md](D:/Code/Fastapi/AgentNews/docs/interview-storyline.md)
- [final-delivery-checklist.md](D:/Code/Fastapi/AgentNews/docs/final-delivery-checklist.md)

## 2. 为什么还要补 integration test

前面已经有：

- compile check
- smoke check
- frontend build

但这些主要解决的是：

- 项目还能不能启动
- 关键路由是不是还活着
- 构建链路有没有断

它们还不够覆盖“像产品一样工作的主链路”，尤其是这几类：

- 会话启动
- 发送一轮 AI 对话
- 会话列表刷新
- 会话恢复
- 删除会话

这些都是这轮前端会话窗口管理非常依赖的能力，所以需要补一层更贴近真实产品链路的 integration test。

## 3. integration_api.py 验证了什么

这份测试没有去打真实外部模型，而是把底层 Agent 执行引擎替换成稳定的 fake 响应，再验证外层业务主链路。

它会检查：

1. `POST /api/ai/session/start`
2. `POST /api/ai/chat`
3. `GET /api/ai/session/{sessionId}`
4. `GET /api/ai/sessions`
5. 再创建第二个 session
6. 再发送第二轮对话
7. 删除第一个 session
8. 再确认会话列表已经移除

它关注的不是模型回答质量，而是：

- 会话状态是否真正写入
- 会话索引是否真正更新
- 标题、预览、消息数是否能跟着刷新
- 删除是否能同步反映到列表

## 4. 为什么 fake 的位置选在 LangGraph 执行层

这一步没有直接 mock 掉 `/api/ai/chat` 路由，也没有直接 mock 掉 `news_agent_service.chat`。

原因是我要尽量保留这条链路：

`router -> news_agent_service -> agent_memory_service -> session index update`

所以我 mock 的是更底层的 `langgraph_agent_service.chat`，这样可以保住：

- 会话准备
- 会话持久化
- memory summary 回写
- session list 更新

这比只验证“接口能返回 200”更接近真实主链路。

## 5. 为什么把它接进 dev-check 和 CI

现在 repo 级 `dev-check` 已经从 3 步变成 4 步：

1. backend targeted compile
2. backend smoke
3. backend integration
4. frontend build

CI 也同步跑这一层。这样后面你继续改会话、AI 页或记忆逻辑时，更容易第一时间发现回归。

## 6. 这一轮对 GitHub 和面试有什么价值

功能做完之后，真正能拉开差距的不是再多一个 Agent 节点，而是：

- 你能不能证明这套链路是可验证的
- 你能不能把材料组织得像一个正式项目

所以这一轮补的展示材料，目标不是“文档更多”，而是：

- README 能快速讲清项目
- demo script 能直接拿去演示
- interview storyline 能直接拿去口头讲
- final checklist 能在上传 GitHub 前做最后核对

## 7. 面试里怎么讲这一步

推荐表述：

在项目后期，我没有继续无上限堆功能，而是开始补交付层能力。一方面我增加了接口级 integration test，专门验证会话启动、AI 对话、会话索引更新、会话恢复和删除这条业务主链路；另一方面我把 README、演示脚本、答辩主线和交付清单整理成了统一材料，让项目不只是“能跑”，而是“可展示、可验证、可交付”。
