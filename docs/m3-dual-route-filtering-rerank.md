# M3.10 双路过滤与最终排序：在 Planner 和回答之间再加一层控制

## 这一阶段为什么要做

到 `M3.9` 为止，项目已经具备：

- Retrieval Planner
- 本地 lexical baseline
- Qdrant 本地向量召回
- 本地 hybrid retrieval
- Tavily Web Search
- 跨源融合与 grounded answer

但仍然还有一个工程问题：

**“拿到了结果”不等于“这些结果都适合直接进入最终回答”。**

更具体地说，当时的缺口包括：

1. `local-first / hybrid / web-first` 虽然已经决定了检索路径，但不同路径下对结果质量的要求还没有显式区分
2. 本地与 Web 两路结果虽然会进入融合，但在融合前缺少一层 route-aware 的过滤
3. 最终排序虽然已经有融合逻辑，但还没有明确把“本地 hybrid 信号”“跨源支持”这些信息纳入运行时可观察状态

所以 `M3.10` 的目标是：

**在 Retrieval Planner 和最终 grounded answer 之间，再补一层双路过滤与最终排序控制。**

---

## 这一阶段做了什么

### 1. 新增双路过滤层

新增：

- `backend/services/dual_route_filter_service.py`

这层负责：

- 在 `local-first / hybrid / web-first` 不同计划下，对本地和 Web 结果分别做 route-aware filtering
- 控制每一路保留多少条
- 控制阈值
- 控制 Web 域名重复上限

这意味着现在不是“检索完了就全扔给融合层”，而是：

```text
Planner
-> Retrieval
-> Route-Aware Filtering
-> Final Rerank / Fusion
-> Grounded Answer
```

### 2. 最终排序显式升级成 plan-aware cross-source rerank

`retrieval_fusion_service.py` 现在除了原有融合逻辑，还把这些信息更明确地纳入了最终排序：

- 当前检索计划
- 本地来源是否带 `lexical + vector`
- Web 来源是否有域名
- 跨源互证

同时把运行时状态显式化成：

- `finalRerankStrategy = plan-aware-cross-source`

### 3. 本地 hybrid 信号继续进入最终排序

在 `M3.9` 里，一条本地新闻已经可能带上：

- `lexical`
- `vector`
- `lexical + vector`

这一步进一步利用了这个信息：

- 如果一条新闻本地同时被 lexical 和 vector 命中，会在最终排序里继续加分

这样做是合理的，因为这代表它同时满足：

- 关键词精确匹配
- 语义相似匹配

### 4. 运行时状态更完整

`/api/ai/status` 现在会返回更多调试信息：

- `localHybridStrategy`
- `dualRouteFilterStrategy`
- `finalRerankStrategy`
- `embeddingConfigMode`

前端 AI 页也会直接显示：

- `本地融合`
- `双路过滤`
- `最终排序`

这样你后面演示时，能更清楚说明系统每一层到底在做什么。

---

## 技术名词解释

### 1. Route-Aware Filtering

意思是：

**同一批检索结果，在不同检索计划下，过滤规则不一样。**

例如：

- `local-first`
  - 对本地结果更宽容
  - 对 Web 结果更保守

- `web-first`
  - 对 Web 结果更宽容
  - 对本地结果更保守

- `hybrid`
  - 两边相对平衡

这一步的核心不是“提升召回”，而是“让进入最终回答的证据更符合当前计划”。

### 2. Final Rerank

`rerank` 就是“拿到候选结果之后，再做一次排序”。

这里的 `final rerank` 不是本地 lexical/vector 内部的融合，而是：

- 本地候选
- Web 候选

在最终进入 prompt 之前，统一再排一次序。

### 3. Cross-Source

`cross-source` 的意思是：

排序时不只看单条来源自身，还看：

- 它是否和其他来源形成互证
- 本地和 Web 是否在讲同一个事件

这一步对新闻问答特别重要，因为新闻场景里：

- 单来源可能不稳定
- 多来源共识更可信

---

## 为什么这一阶段重要

如果没有这一层，系统虽然已经能回答，但还是会有两个风险：

1. 弱相关结果进入最终回答  
   导致回答看起来“来源很多”，但证据集质量一般。

2. Planner 和最终答案之间缺少真正的执行约束  
   也就是说，虽然系统说自己是 `local-first`，但最终证据集未必真的体现了这种偏好。

而 `M3.10` 做完后，系统第一次真正具备：

- 显式检索计划
- route-aware filtering
- final rerank
- grounded answer

这已经非常接近一个正式的受控检索工作流了。

---

## 当前这一步的工程价值

这一步很适合你后面在面试里这样讲：

“我没有让 Planner 只停留在标签层，而是继续补了一层 route-aware filtering 和 final rerank。这样 local-first、hybrid、web-first 不只是名字不同，而是会影响最终哪些证据被保留、怎么排序，最后再进入 grounded answer。” 

这句话的价值很高，因为它说明：

- 你不是只会搭概念图
- 你把 Planner 真正落到了执行层
- 你知道检索工作流里，检索之后还有过滤和 rerank

---

## 这一阶段怎么测试

### 1. 看状态

访问：

- `GET /api/ai/status`

预期会多出：

- `dualRouteFilterStrategy = route-aware-filtering`
- `finalRerankStrategy = plan-aware-cross-source`

AI 页顶部也应看到：

- `双路过滤 Route-Aware`
- `最终排序 Cross-Source`

### 2. 测三类问题

#### local-first

问题示例：

- `根据本地新闻库总结一下科技热点`

预期：

- 计划是 `local-first`
- 本地来源更容易保留更多条

#### web-first

问题示例：

- `今天最新的卫星发射计划有什么进展`

预期：

- 计划是 `web-first`
- Web 来源更容易排前

#### hybrid

问题示例：

- `最近科技新闻里哪些变化最可能影响大模型行业`

预期：

- 计划是 `hybrid`
- 本地和 Web 两边都能留下来

### 3. 看本地来源标签

在本地新闻来源卡片里，继续看：

- `lexical`
- `vector`
- `lexical+vector`

这一步和 `M3.9` 配合起来，能帮助你判断：

- 是本地 hybrid 在工作
- 还是双路过滤 / 最终排序在工作

---

## 和后续 LangGraph 的关系

`M3.10` 完成之后，系统的受控工作流更接近：

```text
Planner
-> Local Retrieval / Web Search
-> Route-Aware Filtering
-> Final Rerank
-> Grounded Generation
```

这已经非常接近后续 `LangGraph` 节点化拆分的自然形态了。

后面如果继续升级：

- `Planner` 可以变成 LangGraph 节点
- `Filtering` 可以变成单独节点
- `Rerank` 可以继续增强
- `Verifier` 也可以继续补进来

所以这一步不是临时补丁，而是在给后续节点化工作流打地基。
