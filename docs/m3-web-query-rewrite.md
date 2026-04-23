# M3.5 Web Query Rewrite

## 问题

在接入 Tavily 之后，系统表面上已经具备了 Web Search 能力，但实际使用里暴露出一个关键问题：

- 用户的问题大多是中文
- Tavily 对部分中文查询会直接返回 `400 Query is invalid`
- 结果就是 Web Search 已开启，但很多中文问题实际上拿不到任何网页来源

这会直接影响两个体验：

1. 用户会觉得“明明开了联网搜索，但还是只有本地结果”
2. 项目在面试里也会被追问：既然你接了 Web Search，为什么中文问题没有发挥作用

## 这次为什么这样做

这次没有把问题简单归因成“检索排序不合理”，而是先处理更底层的一层：

- Web Search 的输入查询本身不适合当前搜索引擎

所以这一阶段新增的是：

- `Web Query Rewrite`

也就是在调用 Tavily 前，先把中文新闻问题改写成简洁英文搜索词，再交给 Web Search。

这一步有两个价值：

1. 它直接提升了 Web Search 的可用性
2. 它天然就是后续 LangGraph 工作流里的 `Query Rewrite` 节点雏形

## 实现原理

### 1. 新增独立的 Query Rewrite 服务

新增：

- `backend/services/query_rewrite_service.py`

它负责：

- 判断当前问题是否包含中文
- 如果包含中文，则调用模型把问题改写成一条简洁英文搜索 query
- 输出只保留单行英文查询，不带解释文字

当前改写 prompt 的目标很明确：

- 保留实体
- 保留事件
- 保留时间/地点线索
- 压缩成适合搜索引擎的英文 query

例如：

- `卫星发射计划`
- 改写后会得到类似 `satellite launch schedule`

### 2. Tavily 检索变成两段式

现在 `backend/services/tavily_service.py` 的流程是：

1. 判断问题是否需要改写
2. 如果需要，先生成英文搜索 query
3. 优先用改写后的 query 调 Tavily
4. 如果改写失败，再回退到原始 query

这样做的原因是：

- 对中文问题，改写后的英文 query 更可能得到稳定结果
- 对英文问题，不需要额外引入一次重写开销

### 3. Web 结果解析放宽

这一阶段顺手修了另一个容易漏掉的问题：

之前 Tavily 结果如果：

- 有标题
- 有 URL
- 但 `content` 为空

就会被系统直接丢弃。

现在改成：

- 只要有标题或 URL，就允许进入候选集
- 如果 `content` 为空，就退回用 `raw_content` 或标题做 snippet

这能避免“Web 明明有结果，却被我们自己过滤掉”的情况。

## 为什么这是合理演进

这一步非常适合作为面试里的方法演进点，因为它说明：

- 不是所有搜索引擎都能直接吃中文问句
- 多语言场景下，Query Rewrite 本身就是检索系统的一部分
- Web Search 不是“接个 API 就结束”，还要考虑输入分布、语言适配和工具边界

你可以这样概括：

“我在接入 Tavily 之后发现，中文新闻问题并不总能直接命中 Web Search。于是我补了一层 Web Query Rewrite，把中文问题先改写成英文搜索词，再交给 Tavily。这一步既解决了实际召回问题，也自然演进成了后续 LangGraph 工作流里的 Query Rewrite 节点。” 

## 手动测试

1. 确保 `.env` 中配置了 `TAVILY_API_KEY` 和 `LLM_API_KEY`
2. 重启后端
3. 在 AI 页提问中文新闻问题，例如：
   - `卫星发射计划`
   - `最近国际油价变化`
   - `大模型融资动态`
4. 预期结果：
   - 不再因为中文 query 被 Tavily 判定无效而丢失 Web 来源
   - 如果本地新闻不足，应看到 Web 来源卡片
   - 在本地无命中的情况下，更容易得到 Web-only 或 Hybrid 的回答

## 意义

这一阶段的意义是：

- 把 Tavily 从“名义上已接入”推进到“中文场景下真正可用”
- 补齐多语言 Web Search 的工程细节
- 为后续 `Query Rewrite -> Retrieval Planner -> Hybrid Retrieval` 铺路

## 下一步

后续建议继续推进：

- 记录 rewrite 前后的 query，便于调试
- 对本地检索和 Web 检索做更明确的 source preference 策略
- 把 Query Rewrite 正式纳入 LangGraph 工作流
