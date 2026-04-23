# M3 会话记忆与摘要记忆

## 1. 这一轮做了什么

这一轮补的是新闻助手的 `session memory`，不是简单把前端历史消息继续往后传。

当前实现包括：

- `sessionId` 驱动的会话隔离
- Redis 持久化的短期会话记忆
- 超出窗口后的摘要记忆 `summary memory`
- 会话恢复、会话清空接口
- prompt 中的记忆注入

对应实现位置：

- [backend/services/agent_memory_service.py](D:/Code/Fastapi/AgentNews/backend/services/agent_memory_service.py)
- [backend/routers/ai.py](D:/Code/Fastapi/AgentNews/backend/routers/ai.py)
- [backend/prompts/news_assistant.py](D:/Code/Fastapi/AgentNews/backend/prompts/news_assistant.py)
- [frontend/src/api/ai.js](D:/Code/Fastapi/AgentNews/frontend/src/api/ai.js)
- [frontend/src/views/AIChat.vue](D:/Code/Fastapi/AgentNews/frontend/src/views/AIChat.vue)

## 2. 为什么这样做

前面项目里已经有“页面级 history”，但那不等于真正的记忆。

页面级 history 的问题：

- 刷新页面就容易丢
- 只能依赖前端带回来
- 不适合后端统一控制上下文窗口
- 不能自然扩展为后续的记忆管理策略

所以这一轮我补的是后端主导的会话记忆。

但这里没有直接做“长期用户画像”或“跨会话偏好记忆”，原因也很明确：

- 新闻助手当前更需要的是同一轮会话延续，而不是长期人格
- 长期记忆更容易引入隐私、脏数据和召回污染问题
- 对这个项目来说，短期会话记忆更实用，也更好讲清楚

## 3. 当前记忆设计

### 3.1 用了什么后端存储

用的是 `Redis`。

原因：

- 你项目本来就已经有 Redis
- 会话记忆天然适合 `TTL` 管理
- 读写频率高、结构相对简单
- 很适合做短期状态缓存

### 3.2 存了什么

每个 `sessionId` 会存一份会话状态，大致包含：

- `sessionId`
- `summary`
- `messageCount`
- `updatedAt`
- `recentMessages`

其中：

- `recentMessages` 保存最近几轮原始消息
- `summary` 保存被压缩后的历史摘要

### 3.3 为什么要“最近消息 + 摘要”

如果只存完整历史，问题会越来越明显：

- prompt 越来越长
- 成本越来越高
- 噪音越来越多
- 老问题会干扰新问题

所以当前设计是：

- 保留最近 `N` 条消息做原始上下文
- 更早的消息滚动压缩成 `summary`

这就是一个很典型的 `short-term memory + summary memory` 方案。

## 4. 当前摘要是怎么做的

这版摘要不是模型生成摘要，而是 `heuristic rollup`。

也就是：

- 抽历史里的用户问题
- 抽历史里的回答结论
- 做一个受控拼接和长度裁剪

我这样做是有意的，因为它有几个优点：

- 不增加额外模型调用成本
- 行为稳定
- 方便调试
- 方便后续再升级成模型摘要

所以面试时你可以很准确地说：

我先实现的是成本更低、可控性更强的 heuristic summary memory，后面如果要继续提升，可以把摘要生成替换成专门的 summarizer chain。

## 5. 记忆是怎么进 prompt 的

当前 prompt 结构变成：

1. system prompt
2. memory summary block
3. recent history
4. 当前用户问题 + sources + query analysis

这里要注意：

`memory summary` 只是用来延续上下文，不是证据。

也就是说：

- 新闻事实仍然必须来自检索到的 sources
- 记忆不能替代 grounded evidence

这点很关键，因为它能避免面试官追问你“记忆会不会造成幻觉放大”时你答不上来。

## 6. 这套方案的边界

当前它解决的是：

- 同一会话的上下文延续
- 页面刷新后的会话恢复
- prompt 窗口受控

它没有解决的是：

- 跨用户长期偏好建模
- 跨会话长期知识沉淀
- 复杂的 memory retrieval

所以这版最准确的定位是：

**会话级短期记忆，不是长期个性化记忆系统。**

## 7. 你后面可以怎么讲

推荐表述：

我在新闻 Agent 里补了一层后端主导的 session memory。具体做法是用 Redis 保存会话状态，把最近几轮消息保留为原始上下文，把更早的对话滚动压缩成 summary memory，再把这个摘要作为上下文补充注入 prompt。这样既能支持多轮对话延续，又不会让 prompt 无限制膨胀。为了保证新闻回答的真实性，我把记忆限定为“上下文延续”，不让它替代检索证据。
