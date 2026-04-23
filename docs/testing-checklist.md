# AgentNews 逐步测试清单

## 使用方式

这份清单用于你每次改完功能后，按顺序验证项目是否还处在可运行状态。

建议使用方式：

1. 先做环境与状态检查
2. 再测新闻主链路
3. 再测缓存与热榜
4. 再测 AI 助手 / 检索 / 向量索引
5. 最后做一次前后端整体回归

---

## 一、环境与启动检查

### 1. 后端环境

确认：

- 根目录 `.env` 已存在
- `MYSQL_URL` 正确
- `REDIS_URL` 正确
- `LLM_API_KEY` 正确
- 如果启用 Tavily，`TAVILY_API_KEY` 正确
- 如果启用向量检索，`LOCAL_RETRIEVAL_ENGINE=hybrid-ready`
- 如果启用向量检索，`ENABLE_VECTOR_RETRIEVAL=true`

推荐显式写上：

```env
QDRANT_URL=
QDRANT_LOCAL_PATH=backend/data/qdrant
QDRANT_COLLECTION=agentnews_news_chunks
QDRANT_TIMEOUT_SECONDS=5

EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings
EMBEDDING_API_KEY=你的_key
EMBEDDING_MODEL=text-embedding-v4
```

说明：

- `QDRANT_URL=` 为空是正常的，表示当前使用本地 Qdrant 模式
- `QDRANT_LOCAL_PATH` 指向本地索引目录

### 2. 基础服务

确认：

- MySQL 已启动
- Redis 已启动
- 前端已启动
- 后端已启动

### 3. 编译检查

建议每次较大改动后执行：

- 后端：`python -m compileall backend`
- 前端：`npm run build`

通过说明：

- 至少没有明显语法错误
- 前端可以正常打包

---

## 二、新闻主链路检查

### 1. 分类页

验证：

- 首页分类 tab 正常显示
- 分类切换能刷新新闻流

### 2. 新闻详情

验证：

- 点击新闻能进入详情页
- 正文、标题、时间、阅读量正常
- 相关推荐能跳到下一篇

### 3. 收藏 / 历史

验证：

- 收藏新增 / 取消正常
- 历史页能记录最近浏览
- 删除单条 / 清空全部正常

---

## 三、缓存与热榜检查

### 1. 分类 / 列表缓存

验证方式：

- 连续请求分类接口两次
- 连续请求新闻列表接口两次

预期：

- 第二次命中更快
- Redis 挂掉时接口仍能回源 MySQL

### 2. 浏览量增量

验证方式：

- 连续刷新同一条新闻详情多次

预期：

- 前端看到的 `views` 会增长
- 一段时间后 MySQL 中的 `views` 会被回刷补齐

### 3. 热榜接口

验证方式：

- 多次访问某一新闻
- 再请求：
  - `GET /api/news/hot?limit=5`
  - `GET /api/news/hot?categoryId=1&limit=5`

预期：

- 刚刚高频访问的新闻排序更靠前

---

## 四、AI 助手状态检查

### 1. 状态接口

访问：

- `GET /api/ai/status`
- `GET /api/ai/index/status`

重点检查字段：

- `promptVersion`
- `plannerEnabled`
- `localRetrievalLabel`
- `localHybridStrategy`
- `dualRouteFilterStrategy`
- `finalRerankStrategy`
- `vectorRetrievalActive`
- `embeddingConfigured`
- `embeddingConfigMode`
- `indexSyncReady`

如果当前向量链路正常，预期应接近：

- `localRetrievalLabel = lexical-plus-qdrant`
- `localHybridStrategy = weighted-rrf`
- `dualRouteFilterStrategy = route-aware-filtering`
- `finalRerankStrategy = plan-aware-cross-source`
- `vectorRetrievalActive = true`
- `embeddingConfigured = true`
- `embeddingConfigMode = explicit` 或 `llm-fallback`
- `indexSyncReady = true`

### 2. AI 页顶部状态

打开 AI 页，顶部应能看到：

- `Prompt news-assistant-v6-route-filter-rerank`
- `Planner 已开启`
- `本地引擎 lexical-plus-qdrant`
- `向量 已激活`
- `索引 可同步`
- `Embedding 显式配置 / LLM 回退`
- `本地融合 Weighted RRF`
- `双路过滤 Route-Aware`
- `最终排序 Cross-Source`

---

## 五、向量索引检查

### 1. 预览切块

访问：

- `GET /api/ai/index/preview/1`

预期：

- 返回 `chunkCount`
- 能看到 `snippet / text / charCount`

### 2. Dry Run

请求：

`POST /api/ai/index/sync`

```json
{
  "dryRun": true,
  "limit": 5
}
```

预期：

- 返回多少条新闻、多少个 chunk
- 不真正写入索引

### 3. 真实同步

请求：

```json
{
  "dryRun": false,
  "newsIds": [1, 2, 3]
}
```

预期：

- `status = synced`
- `upsertedPoints` 有值
- `vectorSize` 有值

---

## 六、本地检索检查

### 1. lexical 检索

输入：

- 带有强实体词的问题
- 直接复述新闻标题的问题

预期：

- 更容易命中本地新闻
- 来源标签更容易出现 `lexical`

### 2. vector 检索

输入：

- 不直接复述标题，而是换一种语义表达

预期：

- 仍然能命中相近新闻
- 来源标签可能出现 `vector`

### 3. local hybrid

输入：

- 既包含标题近似，又包含语义改写的问题

预期：

- 来源标签更容易出现 `lexical+vector`

---

## 七、Tavily 与双路检索检查

### 1. Tavily 状态

如果配置了 `TAVILY_API_KEY`，预期：

- `webSearchEnabled = true`
- AI 页显示 `Tavily 已开启`

### 2. 中文 Web Query Rewrite

输入：

- `卫星发射计划`
- `最近国际油价变化`
- `大模型融资动态`

预期：

- 即便是中文问题，也能更容易拿到 Web 来源

### 3. 三种检索计划

测试问题：

- `根据本地新闻库总结一下科技热点`
  - 预期：`local-first`

- `今天最新的卫星发射计划有什么进展`
  - 预期：`web-first`

- `最近科技新闻里哪些变化最可能影响大模型行业`
  - 预期：`hybrid`

---

## 八、最终回答与来源检查

每次 AI 回答后，重点看：

- 是否返回 `retrievalPlan`
- 是否返回 `strategy`
- 是否返回 `confidence`
- 是否返回 `sources`
- 本地来源是否能跳详情页
- Web 来源是否能打开外链

对来源卡片特别看：

- 时间
- 域名
- `lexical / vector / lexical+vector / web`
- 综合分数

---

## 九、问题排查提示

### 1. `QDRANT_URL` 留空

这是正常的，表示当前使用本地 Qdrant 模式，不影响功能。

### 2. `Embedding` 显示 `LLM 回退`

说明当前 embedding 没有显式配置，而是沿用了聊天模型配置。

不是错误，但如果你想让配置更清楚，建议显式补上 `EMBEDDING_*`。

### 3. `索引 可同步` 但检索没命中

先确认：

1. 是否真的执行过 `dryRun=false` 的同步
2. 提问的新闻是否已经被索引
3. 提问是否更偏 lexical、vector 或 Web

### 4. 重启后端后状态没变

优先检查：

- 修改的是根目录 `.env`，不是 `.env.example`
- 后端是否真的重启了

---

## 十、建议回归顺序

每次大改后，建议按这个顺序回归：

1. `python -m compileall backend`
2. `npm run build`
3. `/api/ai/status`
4. `/api/ai/index/status`
5. `/api/ai/index/preview/1`
6. `/api/ai/index/sync` dry-run
7. `/api/ai/index/sync` 真实同步
8. 首页 / 详情 / 收藏 / 历史
9. AI 页三类问题：
   - local-first
   - hybrid
   - web-first

按这套顺序，基本能比较快定位是：

- 配置问题
- 索引问题
- 检索问题
- 前端展示问题

---

## 十一、Verifier 与抗幻觉检查

### 1. 状态接口

访问：

- `GET /api/ai/status`

重点确认：

- `verifierEnabled = true`
- `verifierStrategy = rule-based-post-verifier`

AI 页顶部应显示：

- `Verifier Rule-Based`

### 2. 无证据拒答

输入一个本地和 Web 都难以命中的问题。

预期：

- `verificationStatus = refused`
- `evidenceLevel = none`
- `guardrailApplied = true`

### 3. 低置信度回退

输入一个只命中少量来源、或者只有 1 条弱 Web 来源的问题。

预期：

- `verificationStatus = guarded`
- `evidenceLevel = weak`
- `guardrailApplied = true`

并且回答正文前面会出现更保守的提醒，而不是直接给出强结论。

### 4. 正常通过

输入一个来源较多、且本地与 Web 互相支撑的问题。

预期：

- `verificationStatus = accepted`
- `guardrailApplied = false`
- `evidenceLevel = moderate` 或 `strong`

---

## 十二、Query Analysis 与 Formatter 检查

### 1. 状态接口

访问：

- `GET /api/ai/status`

重点确认：

- `queryAnalysisEnabled = true`
- `queryAnalysisStrategy = heuristic-query-analysis`
- `responseFormatterEnabled = true`
- `responseFormatterStrategy = evidence-aware-followups`

### 2. AI 页顶部状态

打开 AI 页后，顶部应出现：

- `Analysis Heuristic`
- `Formatter Follow-Ups`

### 3. 回答内的问题分析

输入三类问题：

- `根据本地新闻库总结一下科技热点`
- `今天最新的卫星发射计划有什么进展`
- `最近科技新闻里哪些变化最可能影响大模型行业`

预期每条回答都能看到：

- `意图`
- `时效`
- `范围`
- `分析说明`

### 4. 追问建议

每条回答应出现 1 到 3 条追问建议。

点击任意建议，预期：

- 会直接发起新一轮对话
- 不需要手动复制建议文本

---

## 十三、Stateful Workflow 与执行轨迹检查

### 1. 状态接口

访问：

- `GET /api/ai/status`

重点确认：

- `workflowEnabled = true`
- `workflowStyle = stateful-node-pipeline`
- `workflowNodes` 至少包含：
  - `query-analysis`
  - `retrieval-planner`
  - `retrieval`
  - `route-filter`
  - `final-rerank`
  - `generator`
  - `verifier`
  - `response-formatter`

### 2. AI 页顶部状态

打开 AI 页，应看到：

- `Workflow Stateful`

### 3. 回答内工作流摘要

问任意问题，回答里应出现：

- `工作流：query-analysis -> retrieval-planner -> ...`

### 4. 回答内执行轨迹

每条回答应看到若干 trace 行，能体现每个节点：

- 做了什么
- 当前状态是 `完成 / 保护 / 回退`

### 5. 场景差异

重点对比：

- 正常命中场景
- 低置信度回退场景
- 无证据拒答场景

预期 trace 中 `verifier` 的状态会不同。
---

## 十四、LangSmith SDK Tracing 检查
### 1. 环境变量

确认根目录 `.env` 中已配置：

- `LANGSMITH_TRACING=true`
- `LANGSMITH_API_KEY=...`
- `LANGSMITH_PROJECT=agentnews-dev`

### 2. 状态接口

访问：

- `GET /api/ai/status`

重点确认：

- `langsmithReady = true`
- `langsmithSdkInstalled = true`
- `langsmithConfigured = true`

### 3. 实际问答

发起一轮 AI 问答后，检查：

- 前端回答中有 `Trace / Run`
- `GET /api/ai/runs/recent` 有新记录
- 本地 `agent_runs.jsonl` 有新记录
- LangSmith 平台能看到对应 trace

---

## 十五、LangGraph StateGraph 检查
### 1. 环境变量

确认根目录 `.env` 中：

- `AGENT_WORKFLOW_ENGINE=langgraph`

### 2. 状态接口

访问：

- `GET /api/ai/status`

重点确认：

- `workflowEnabled = true`
- `workflowEngine = "langgraph"`
- `workflowStyle = "langgraph-stategraph"`
- `graphVisualizationReady = true`

### 3. AI 页顶部状态

打开 AI 页，顶部应看到：

- `Workflow LangGraph`
- `Graph Ready`

### 4. LangSmith 图视图

发起一轮 AI 问答后，在 LangSmith 平台检查：

- 是否能看到 `AgentNews Workflow`
- 是否能看到节点执行链路
- 节点中应包含：
  - `query-analysis`
  - `retrieval-planner`
  - `retrieval`
  - `route-filter`
  - `final-rerank`
  - `generator`
  - `verifier`
  - `response-formatter`
  - `no-evidence-response`（在无证据场景下）

---

## 十六、Workflow Graph Export 检查
### 1. 图结构接口

访问：

- `GET /api/ai/workflow/graph`

重点确认：

- `engine = "langgraph"`
- `style = "langgraph-stategraph"`
- `graphVisualizationReady = true`

### 2. 节点与边

返回里应看到：

- `nodes`
- `edges`
- `mermaid`

节点中应至少包含：

- `__start__`
- `query-analysis`
- `retrieval-planner`
- `retrieval`
- `route-filter`
- `final-rerank`
- `generator`
- `verifier`
- `response-formatter`
- `no-evidence-response`
- `__end__`

### 3. Mermaid

把 `mermaid` 文本复制到支持 Mermaid 的 Markdown 环境里，应能渲染流程图。

---

## 十七、Evaluation Baseline 检查
### 1. 评测集

访问：

- `GET /api/ai/eval/dataset`

应看到预置评测样本。

### 2. 跑基线评测

请求：

- `POST /api/ai/eval/run`

示例 body：

```json
{
  "limit": 6
}
```

### 3. 结果字段

重点确认：

- `plannerAccuracy`
- `intentAccuracy`
- `freshnessAccuracy`
- `scopeAccuracy`
- `results`

### 4. 单条 case

每个 `result` 里应包含：

- `actualPlan / expectedPlan`
- `actualIntent / expectedIntent`
- `actualFreshness / expectedFreshness`
- `actualScope / expectedScope`
- `mismatches`

### 5. 环境影响

如果 `TAVILY_API_KEY` 未启用，`webEnabled` 会影响 planner 结果。  
所以建议在 Tavily 已开启的环境下跑这组 baseline。

---

## 十八、Evaluation Feedback Loop 检查
### 1. 跑一次评测

请求：

- `POST /api/ai/eval/run`

### 2. 查看最近评测 run

访问：

- `GET /api/ai/eval/runs/recent`

应看到：

- `runId`
- `recordedAt`
- `totalCount`
- `passedCount`
- `plannerAccuracy`
- `intentAccuracy`
- `freshnessAccuracy`
- `scopeAccuracy`

### 3. 查看最近失败 case

访问：

- `GET /api/ai/eval/failures/recent`

应看到：

- `caseId`
- `title`
- `mismatches`
- `expectedPlan / actualPlan`
- `expectedIntent / actualIntent`
- `expectedFreshness / actualFreshness`
- `expectedScope / actualScope`

### 4. LangSmith Evaluation 状态

访问：

- `GET /api/ai/eval/langsmith/status`

重点确认：

- `langsmithReady`
- `langsmithConfigured`
- `datasetUploadReady`
- `defaultDatasetName`

### 5. LangSmith Export

访问：

- `GET /api/ai/eval/langsmith/export`

应看到：

- `datasetName`
- `exampleCount`
- `examples`

### 6. LangSmith Sync

请求：

- `POST /api/ai/eval/langsmith/sync`

如果当前 LangSmith 已配置，预期：

- `synced = true`
- 返回 `datasetId`

如果未配置，预期：

- `synced = false`
- `note` 说明当前仅支持本地导出
