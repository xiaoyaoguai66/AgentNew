# M3.9 本地 Hybrid Retrieval：把 lexical + qdrant 从简单拼接升级成正式融合

## 这一阶段为什么要做

`M3.8` 完成之后，项目已经具备了：

- lexical baseline
- Qdrant 本地向量召回
- `hybrid-ready` 模式

但当时本地双路召回还有一个明显问题：

**lexical 和 vector 只是“都拿到了”，但还没有被正式融合。**

更具体地说，当时的问题包括：

1. 两路结果只是按分数简单拼接  
   这会导致：
   - score 尺度不统一
   - 一路结果容易把另一路挤掉
   - 很难解释“为什么这一条排前面”

2. 向量结果是 chunk 级，而不是 news 级  
   同一条新闻如果多个 chunk 都命中，就可能重复出现多次。

3. 没法清楚看出一条来源到底是：
   - lexical 命中
   - vector 命中
   - 两者都命中

所以 `M3.9` 的目标不是继续加新基础设施，而是：

**把本地双路召回正式做成可解释的 hybrid retrieval。**

---

## 这一阶段做了什么

### 1. 新增本地 hybrid 融合服务

新增：

- `backend/services/local_hybrid_retrieval_service.py`

这层专门负责把本地：

- lexical sources
- vector sources

融合成最终本地候选集。

### 2. 融合方式从简单拼接升级成加权融合

当前本地 hybrid 融合不再只是：

- lexical 前几条
- vector 前几条
- 去重

而是综合考虑：

1. rank 权重
2. lexical 原始分数
3. vector 原始分数
4. query 和来源的词项重叠
5. 发布时间新鲜度
6. 一条新闻是否被 lexical 和 vector 同时命中

这意味着现在的本地 hybrid 更像：

**Weighted RRF + overlap boost + recency boost + dual-signal bonus**

而不是简单的 append。

### 3. 向量结果先聚合到 news 级

`vector_news_retriever.py` 现在会先把 chunk 级结果聚合成新闻级结果：

- 同一新闻的多个 chunk 命中时，只保留一条来源
- 保留得分最高的 chunk 作为展示 snippet
- 如果同一新闻被多个 chunk 命中，会给一点额外加分

这一步很关键，因为用户最终要看的来源单位是“新闻”，不是“chunk”。

### 4. 每条来源会带上检索通道标签

现在 `AiSourceItem` 多了：

- `retrievalTags`

例如：

- `["lexical"]`
- `["vector"]`
- `["lexical", "vector"]`
- Web 来源是 `["web"]`

这样你后面不只是知道“命中了哪条新闻”，还知道：

**它到底是靠哪种检索方式命中的。**

### 5. Embedding 配置模式显式化

这一步还顺手补了：

- `embeddingConfigMode`

当前后端会明确区分：

- `explicit`
- `llm-fallback`
- `partial`
- `missing`

前端 AI 页也会直接显示当前 embedding 的配置模式。

这一步主要是为了工程可解释性，不是为了召回本身。

---

## 这里涉及的技术含义

### 1. Hybrid Retrieval

`hybrid retrieval` 的意思不是“同时开两个检索器”这么简单，而是：

**把不同召回信号在统一规则下融合成最终候选集。**

在你的项目里，本地 hybrid 指的是：

- lexical retrieval
- vector retrieval

的本地融合，不包含 Tavily Web Search。

### 2. Weighted RRF

`RRF` 是一种很常见的多路检索结果融合思想。

它的核心不是直接比 raw score，而是更看重：

- 结果在各自排序里的位置

因为不同检索器的分数尺度往往不一样，直接拿 raw score 比较很容易失真。

当前这一步不是论文级标准 RRF 复刻，而是一个更贴合本项目的工程版本：

- 用 rank 做主信号
- 再叠加 lexical/raw、vector/raw、overlap、recency 等补充信号

所以这里更准确的说法是：

**Weighted RRF 风格的本地融合。**

### 3. Dual-Signal Bonus

如果同一条新闻同时被：

- lexical 命中
- vector 命中

就说明这条新闻既满足关键词匹配，也满足语义相似。

因此当前融合里会给这种新闻额外加分。

这是一个非常适合面试解释的点，因为它很好理解，也很符合新闻检索场景。

---

## 为什么这样做比之前更适合新闻场景

新闻类问题既有：

- 强实体词问题
- 语义改写问题
- 时效性要求

如果只用 lexical：

- 精准，但容易漏掉表达改写

如果只用 vector：

- 语义强，但容易把实体不够精准的结果排上来

而现在这个本地 hybrid 做到的是：

1. lexical 保持实体命中优势
2. vector 补语义召回
3. 双命中再额外加权
4. 时间较新的新闻有新鲜度加成

这比之前“简单拼接”更像一个正式的本地检索系统。

---

## 这一步怎么测试

### 1. 看状态

打开 AI 页，观察顶部：

- `本地引擎 lexical-plus-qdrant`
- `向量 已激活`
- `Embedding 显式配置 / LLM 回退`
- `本地融合 Weighted RRF`

### 2. 测本地双命中

先确保你已经对至少一条新闻做过真实索引同步，然后问：

- 直接用标题
- 或者同义改写但仍然明显指向这条新闻

预期：

- 来源卡片仍然是“本地新闻”
- 但来源元信息里更容易出现 `lexical+vector`

这说明它不是只靠一种信号命中的。

### 3. 测 lexical-only / vector-only / 双命中

你可以分别尝试：

1. 强关键词问题  
   比如标题里的实体名、机构名、政策名  
   预期更容易偏 lexical。

2. 语义改写问题  
   不直接复述标题，而是换一种问法  
   预期更容易偏 vector。

3. 标题近似 + 语义改写混合  
   预期更容易出现 `lexical+vector`。

---

## 这一阶段在方法演进里的意义

这一阶段很适合你后面面试时解释成：

“我不是一把把 lexical 替换成向量检索，而是先接入 Qdrant，让 vector retrieval 真正跑通；然后又补了一层本地 hybrid retrieval，把 lexical 和 vector 做成正式融合。这样本地检索系统是从单一路径 baseline，演进到多信号融合，而不是简单把一个检索器换成另一个。” 

这句话的价值在于：

- 它强调了方法演进
- 它能解释为什么要先保留 lexical
- 它能解释为什么后续还需要 rerank 和 LangGraph

---

## 下一步

`M3.9` 完成后，后面更自然的方向是：

1. 继续优化本地 hybrid 的 filter 和 rerank
2. 把本地 hybrid 和 Tavily 双路更清楚地分层
3. 再继续往 `LangGraph` 风格工作流推进

也就是说，这一步完成后，你的项目已经不只是“接上了向量库”，而是开始拥有真正意义上的本地 hybrid retrieval。
