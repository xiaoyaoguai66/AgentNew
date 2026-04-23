# M3 会话窗口管理

## 1. 这一轮做了什么

这一轮补的是“像 ChatGPT 网页版一样的会话窗口管理”，不是单纯在前端点一下“新对话”就换一个临时 `sessionId`。

当前实现包括：

- 后端维护会话索引，保存 `sessionId / title / preview / messageCount / updatedAt`
- 前端 AI 页新增左侧会话抽屉，支持查看、切换、删除历史会话
- “新对话”只创建新会话，不会覆盖已有会话
- 删除会话直接在会话窗口里完成；如果删除的是当前会话，会自动切到下一个可用会话，或创建一个新的空会话
- 当前激活会话的标题、预览、消息数会和会话列表保持同步

对应实现位置：

- [backend/services/agent_memory_service.py](D:/Code/Fastapi/AgentNews/backend/services/agent_memory_service.py)
- [backend/routers/ai.py](D:/Code/Fastapi/AgentNews/backend/routers/ai.py)
- [frontend/src/api/ai.js](D:/Code/Fastapi/AgentNews/frontend/src/api/ai.js)
- [frontend/src/views/AIChat.vue](D:/Code/Fastapi/AgentNews/frontend/src/views/AIChat.vue)

## 2. 为什么要单独做“会话窗口管理”

前一阶段已经有 `session memory`，但那解决的是“同一个会话如何延续上下文”，不是“用户如何像主流聊天产品一样管理多个会话窗口”。

两者关注点不同：

- `session memory`
  解决上下文延续、摘要记忆、刷新恢复
- `session window management`
  解决会话列表、切换、删除、保留历史窗口

如果只做前者，用户会遇到两个问题：

- 点“新对话”以后，旧对话没有一个稳定入口可以切回来
- 删除或恢复会话只能依赖前端临时状态，不像成熟聊天产品

所以这一轮是把“后端会话状态”进一步产品化成“前端会话窗口”。

## 3. 当前设计怎么分层

### 3.1 后端层

后端仍然由 `Redis` 承担会话存储，但现在拆成了两类 key：

- `ai session state`
  保存某个会话自己的 `summary / recentMessages / title / preview / messageCount / updatedAt`
- `ai session index`
  保存整个会话列表，用于前端侧栏渲染

这样做的好处是：

- 会话详情和会话列表职责清晰
- 前端拿侧栏列表不需要把所有完整消息都拉下来
- 后面如果要分页、按用户隔离、接数据库落盘，也更容易演进

### 3.2 前端层

前端现在的 AI 页分成两层状态：

- `sessionState`
  当前激活会话的完整状态
- `sessionItems`
  侧栏里的会话列表

切换会话时：

1. 拉取目标 `sessionId` 的详情
2. 恢复最近消息
3. 更新当前激活会话
4. 刷新侧栏 active 状态

删除会话时：

1. 删除后端会话状态和会话索引项
2. 刷新会话列表
3. 如果删除的是当前会话，则自动切换 fallback 会话

## 4. 为什么“新对话”不直接删除旧会话

主流聊天产品的交互约定是：

- “新对话” = 创建一个新的会话窗口
- “删除会话” = 明确删除某个历史窗口

这两个动作不应该混在一起。

所以当前策略是：

- 如果当前只是一个完全空白、还没开始对话的临时会话，可以在新建下一轮时顺手清掉，避免堆积无用空会话
- 只要当前会话里已经有真实消息，就保留在历史列表中

这样既符合产品直觉，也不会产生大量空白窗口。

## 5. 会话标题和预览是怎么来的

当前没有单独做“会话命名模型”，而是用了受控的 heuristic 方案：

- 第一轮用户问题自动截断生成 `title`
- 最近一轮回答的前半段生成 `preview`

这样做的原因是：

- 成本更低
- 行为更稳定
- 不额外依赖模型
- 已经足够接近聊天产品常见的标题生成体验

如果后面要继续升级，可以把 `title` 改成专门的 summarizer 生成，但当前版本不需要先做复杂化。

## 6. 这套设计和记忆能力的关系

这里最容易混淆的是：

- 会话窗口管理不是新的“记忆算法”
- 它是记忆能力的产品化外层

也就是说：

- `summary memory / recent messages`
  决定模型能记住什么
- `session list / switch / delete`
  决定用户怎么操作这些会话

面试里最好把这两个层次分开讲，不要混成“我做了聊天记录，所以这就是 memory”。

## 7. 面试里怎么讲

推荐表述：

我在新闻 Agent 里把会话能力拆成了两层。第一层是后端主导的 session memory，用 Redis 保存最近消息和摘要记忆，解决多轮对话上下文延续。第二层是会话窗口管理，在此基础上增加会话索引、标题预览、切换和删除能力，让前端交互更接近主流聊天产品。这样既保证了模型侧上下文管理，又保证了用户侧会话管理体验。
