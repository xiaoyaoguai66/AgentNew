# AgentNews 方法演进记录

## 目标

这份文档用于记录 AgentNews 在新闻检索与 Agent 架构上的演进过程，不只是记录“最后用了什么”，也记录：

- 为什么先用某种方案
- 某种方案解决了什么问题
- 某种方案的缺点是什么
- 为什么后续要升级

这份记录后续可以直接服务于：

- 项目总结
- GitHub README 补充材料
- 面试时回答“为什么这样设计”

## 第一阶段：轻量级本地检索 baseline

### 方案

先实现一个可解释的本地新闻检索 baseline，用：

- MySQL 候选集
- 主题与时间过滤
- lexical retrieval
- 规则打分

完成 grounded QA。

### 为什么先这样做

原因不是“它最强”，而是“它最适合作为第一阶段基线”：

1. 不引入额外基础设施  
   不需要先部署向量库、embedding 服务和 reranker，直接基于现有 MySQL 和新闻表就能跑通。

2. 可解释性强  
   可以清楚说明命中原因：标题命中、关键词命中、时间更近、热度更高。

3. 适合先建立 grounded QA 闭环  
   先解决“回答必须基于来源”这个问题，再逐步提升召回质量。

4. 方便后续对比升级收益  
   有了 baseline，后面升级到向量检索和混合检索时，才能解释“为什么升级是值得的”。

### 局限

这个阶段的主要问题是：

- 对语义改写和隐式表达不敏感
- 中文切分能力有限
- 复杂问法可能召回不到
- 没有真正的 rerank
- 仍然不具备实时新闻能力

## 第二阶段：升级到混合检索

### 目标

不是简单“把 lexical retrieval 换成向量检索”，而是升级为：

- 稀疏检索
- 向量检索
- 元数据过滤
- rerank

也就是更适合新闻场景的 hybrid retrieval。

### 为什么不是纯向量检索

新闻场景不适合直接只用 dense retrieval，原因包括：

1. 新闻问题有大量强实体词  
   比如公司名、人名、国家名、政策名、事件名，这类内容 lexical retrieval 往往非常重要。

2. 新闻问题很依赖时间和主题过滤  
   仅靠向量相似度，不足以表达“近 24 小时”“只看国际新闻”这类约束。

3. 新闻问答强调可解释和精确匹配  
   纯向量检索可能语义相近但实体不对，这对新闻类应用风险较高。

### 预期方案

后续推荐演进为：

- MySQL / BM25：负责精确关键词召回
- Qdrant：负责 dense retrieval
- metadata filter：负责时间范围、主题范围、来源限制
- rerank：负责最后排序

## 第三阶段：接入实时 web search

### 目标

本地新闻库只能回答“项目内已有数据”的问题，不能覆盖最新事件。

因此后续会加入 Tavily web search，作为第二检索源，用于：

- 最新新闻补充
- 外部事实验证
- 本地新闻库无命中时的补救

### 为什么不一开始就接 Tavily

因为如果本地来源结构、回答协议和 grounded answer 逻辑都还没搭好，过早接入外部搜索会导致：

- 协议频繁变动
- 来源难统一
- 难以解释“回答到底基于什么生成”

所以顺序是：

1. 先做本地 grounded QA
2. 再接 Tavily
3. 再做双路检索融合

### 当前实现记录

当前已经完成了 Tavily 作为第二检索源的接入，但它被设计成可开可关的能力：

- 配置了 `TAVILY_API_KEY` 时，参与双路检索
- 未配置时，系统自动退回仅本地检索

这样做是为了保证：

- 实时能力可以逐步接入
- Web 搜索不会成为系统单点依赖
- 本地新闻平台的核心链路仍然可运行

配置上也明确区分了：

- `.env`：真实运行配置，应用启动时会读取
- `.env.example`：模板文件，只用于说明需要哪些环境变量

这样做是为了避免把真实密钥误提交到仓库。

这一阶段后面还补过一次工程细节修复：

- 最开始 AI 页顶部的 Tavily 状态只会在首轮对话后刷新
- 之后新增 `/api/ai/status`，让页面在打开时先同步一次后端能力状态
- 继续排查后发现 `AIChat` 路由本身开启了 `keepAlive`
- 这意味着用户切到别的 Tab 再回来时，页面不会重新触发 `onMounted`
- 最终把同步逻辑补到了 `onActivated`

这个试错过程本身也值得保留，因为它说明了一个很典型的工程问题：后端配置已经生效，不代表前端展示状态会自动更新，页面生命周期和缓存策略同样会影响最终用户感知。

在 Tavily 接入之后，后面还暴露过另一类工程问题：超时治理。

- 前端原本把所有接口统一设置成 10 秒超时
- 这对新闻列表和详情页没问题，但对“本地检索 + Web 搜索 + 模型生成”的 AI 链路不合适
- 结果就是 Tavily 开启后，用户可能先看到前端 `timeout of 10000ms exceeded`
- 实际上后端不一定真的报错，而是前端先把请求截断了

因此后续又补了一次超时治理：

- 前端给 AI 接口单独放宽超时
- 后端把 Tavily 超时配置化，并在超时时自动降级回本地检索
- 后端把模型请求超时也配置化

这一步对面试也很有价值，因为它能说明：接入一个外部工具不只是“调通接口”，还要考虑工具慢、工具挂、工具超时之后系统如何表现。

在继续使用 Tavily 的过程中，又暴露出一个更底层的问题：中文 query 兼容性。

- Tavily 在部分中文问题上会直接返回 `400 Query is invalid`
- 这意味着系统虽然显示“联网已开启”，但中文问题未必真的拿得到 Web 来源
- 如果不处理这个问题，Web Search 就会停留在“名义上已接入”，而不是“真实可用”

因此又补了一层 `Web Query Rewrite`：

- 先判断问题是否包含中文
- 如果是中文问题，就先改写成简洁英文搜索词
- 再把改写后的 query 交给 Tavily

这一步很关键，因为它把“Web Search 接口可调用”推进到了“中文场景下 Web Search 可用”，也让后续工作流里 `Query Rewrite` 这个节点有了真实工程来源，而不是为了做 Agent 架构图硬加出来的。

## 第三阶段补充：从简单拼接到轻量 Rerank

在接入本地新闻检索和 Tavily 之后，系统一开始只是把两路结果简单拼接：

- 本地结果取前几条
- Web 结果取前几条
- 然后直接作为最终证据集返回

这种做法能快速打通双路检索，但还不算真正的融合，因为它没有解决：

- 不同检索源分数不统一
- 结果先后顺序缺少统一标准
- 证据集缺少来源平衡
- 跨源互证没有被利用

因此后面补了一层轻量融合与初步 rerank：

- 先把本地检索分数和 Tavily 分数映射到统一尺度
- 再综合词项重叠、字符 bigram、新鲜度、来源先验和跨源互证重新排序
- 最后做平衡选源，避免最终证据集被单一来源类型占满

这一步的意义不是“已经完成最终版检索系统”，而是给后续升级到 Qdrant、hybrid retrieval 和真正的 reranker 打好接口基础。

这样在面试里就可以清楚讲出一条更完整的演进路径：

1. 先用可解释的 lexical baseline 建立 grounded QA
2. 再接入 Tavily，补足实时信息
3. 再从简单拼接升级到轻量 rerank，解决多源融合排序问题
4. 最后再升级到更正式的 hybrid retrieval 和 LangGraph 工作流

## 第四阶段：工作流编排升级

### 当前阶段

当前并不是完全自由的思考型 agent，而是一个受控工作流：

- 用户问题输入
- 参数解析
- 本地检索
- 命中判断
- grounded prompt
- LLM 生成
- 返回来源与置信度

### 后续升级方向

后续可以升级为 LangGraph 风格的工作流编排，但不建议直接做“完全自由自治 agent”。

更适合新闻场景的方向是：

- Intent Router
- Query Rewrite
- Retrieval Planner
- Local Retrieval
- Tavily Web Search
- Merge / Rerank
- Grounded Generation
- Verifier
- Response Formatter

### 为什么不是完全自由的思考型 agent

新闻场景最重要的是：

- 真实性
- 可解释性
- 来源约束
- 幻觉控制

完全自由的 agent 虽然更像“会思考”，但对新闻问答来说反而更容易：

- 工具调用不可控
- 过程难解释
- 幻觉更严重

所以更合理的方向是：

受控工作流 + 局部 reasoning + 明确来源约束

## 面试表达建议

可以这样概括这条演进路线：

“我没有一开始就直接上向量检索和完全自由的 agent，而是先做了一个可解释的本地 lexical retrieval baseline，用 MySQL 候选集和规则打分建立 grounded QA 闭环。这样能先解决来源约束和可解释性问题。随后再升级到 Qdrant 混合检索和 Tavily web search，把语义召回、实时信息和来源融合补上。Agent 编排方面，我也不是直接做高自治 agent，而是优先采用受控工作流，让检索、生成和校验链路更适合新闻场景。” 

## 后续维护方式

后续每完成一个阶段，都在这份文档里继续补充：

- 新方案
- 旧方案的不足
- 为什么要升级
- 升级后的收益与代价

## 第七阶段：接入真实 Qdrant 向量召回

在 `M3.6` 和 `M3.7` 完成之后，系统已经具备了：

- 可插拔的本地检索层
- 新闻 chunking
- embedding pipeline
- Qdrant / vector retrieval 的预留接口

但那时最准确的状态仍然是：

- `vector-ready`

而不是：

- `vector-active`

因为当时虽然结构已经搭好，但还没有真正把：

- embedding
- Qdrant collection
- upsert
- query

串成可运行闭环。

因此下一步必须做的不是继续加概念，而是把本地向量检索真正落地。

### 为什么这一阶段用 Qdrant local mode

当前本地环境里，Docker daemon 不可用。

如果此时强行等待容器环境齐全，整条向量检索研发链路会被卡住；但如果直接跳过 Qdrant，又会让“向量检索”停留在纸面设计。

所以这一步选了一个更务实的方案：

- 开发阶段先用 `qdrant-client` 的本地持久化模式
- 跑通真实的 `chunk -> embedding -> index -> query`
- 后续再保留切到独立 Qdrant 服务的能力

这样做的核心思想是：

**先把能力跑通，再把部署形态升级。**

### 这一阶段解决了什么

这一步真正补齐了：

1. Qdrant 客户端接入
2. 本地 collection 初始化
3. 新闻 chunk 向量 upsert
4. query 向量查询
5. payload filter
6. vector sources 映射回 `AiSourceItem`

这意味着本地检索正式从：

- lexical baseline

演进成：

- lexical baseline
- vector retrieval
- local hybrid-ready / vector-active

### 为什么不是按新闻类别选不同 embedding

这一阶段仍然坚持：

- 一套统一 retrieval embedding

而不是：

- 科技一套
- 财经一套
- 国际一套

原因是检索时最重要的是统一向量空间，而不是为每个新闻分类拆分 embedding 模型。分类、时间和来源约束更适合放在 metadata filter 和 rerank 层处理。

### 这一步在方法演进里的意义

这一步之后，你就可以把整条方法演进更准确地讲成：

1. 先做可解释 lexical baseline，保证 grounded QA 和来源约束
2. 再做本地检索 abstraction，避免后续改 Qdrant 时推翻主链路
3. 再接入真实 Qdrant 向量召回，把 `vector-ready` 升级成 `vector-active`
4. 最后继续往更正式的 hybrid retrieval、rerank 和 LangGraph 工作流推进

这比直接说“后来用了向量检索”更完整，也更有工程说服力。

## 第五阶段：显式 Retrieval Planner

在完成本地检索、Tavily、Query Rewrite 和轻量 rerank 之后，系统其实已经具备了双路检索能力，但还缺一个很重要的工作流节点：

- 到底什么时候该先查本地？
- 什么时候该先查 Web？
- 什么时候两边一起查？

如果这一步没有显式建模，系统虽然“能搜”，但仍然属于统一路径下的多源检索，而不是受控工作流。

因此后面又补了一层 `Retrieval Planner`，把问题正式分成：

1. `local-first`
2. `hybrid`
3. `web-first`

这一步很关键，因为它让系统第一次具备了明确的“检索策略决策”能力，而不再只是默认并行搜完再融合。

### 为什么这一步重要

它解决的不是“召回精度”本身，而是“工作流正确性”：

- 对显式限定站内新闻的问题，应该优先用本地库
- 对今天/刚刚/最新这类问题，应该优先走 Web Search
- 对总结、对比、趋势分析类问题，应该同时保留本地与 Web 的互补价值

这让后续的系统演进不再是：

`检索 -> 生成`

而是变成：

`Planner -> Retrieval -> Fusion -> Generation`

### 为什么还不是自由思考型 Agent

即便加入了 Planner，这一阶段仍然不是完全自由的自治 Agent。

原因是新闻场景最重要的不是“看起来会思考”，而是：

- 来源约束
- 真实性
- 可解释
- 可降级

所以这里依然坚持：

**受控工作流 + 显式规划 + grounded answer**

而不是完全黑盒式的高自治 Agent。

### 与后续 Qdrant / LangGraph 的关系

这一层的价值还在于，它让后面升级 Qdrant 混合检索时不需要重新设计总流程：

- 本地检索可以从 lexical baseline 升级成 BM25 / Qdrant
- Planner 节点仍然保留
- Fusion / Rerank 层仍然保留
- 再往后直接接 LangGraph 的节点化编排即可

所以你后面在面试里可以这样讲：

“我不是一开始就把检索做成统一黑盒，而是先让系统具备可解释的 Retrieval Planner。这样后面无论本地检索从 lexical 升级到 Qdrant，还是把整个链路迁到 LangGraph，系统的工作流骨架都能保持稳定。” 

## 第六阶段：把本地检索层做成可插拔结构

在加入 Retrieval Planner 之后，系统的上层工作流已经更稳定了，但本地检索层本身还没有抽象开。

也就是说，虽然我已经明确知道：

- 当前本地检索用的是 lexical baseline
- 后续要升级到 Qdrant / 向量检索

但如果代码层还是只有单一实现，那么后续真的接 Qdrant 时，仍然很容易把已经稳定的主流程一起扰动。

所以后面又补了一步：

**先把本地检索层拆成可插拔结构，再继续推进向量检索。**

这一步的核心不是“功能立刻变强很多”，而是“结构变得可演进”：

- `lexical_news_retriever` 承接当前已稳定的 baseline
- `vector_news_retriever` 作为后续 Qdrant 的独立入口
- `news_retrieval_service` 作为统一 façade

这样以后无论是继续用 lexical，还是接入 Qdrant，都不会直接影响：

- Retrieval Planner
- Fusion / Rerank
- Grounded Prompt
- LLM Generation

这一步很适合面试时解释成：

“我没有在 lexical baseline 刚稳定时就直接把 Qdrant 强塞进主链路，而是先把 retriever 层做成 abstraction。这样系统当前仍然稳定运行，后续真正接向量检索时，主要改动会被限制在 retriever 层内部。” 

这比简单说“后面换成向量检索了”更有工程说服力。

## 第八阶段：把本地 lexical + vector 做成正式 Hybrid Retrieval

在 `M3.8` 之后，系统已经具备了真实的本地向量召回能力，但那时仍然还有一个工程缺口：

- lexical 和 vector 虽然都能返回结果
- 但两者还没有形成正式的本地 hybrid retrieval

当时更接近的状态是：

- 两路结果都拿到了
- 再做一个较保守的拼接和去重

这能让系统先跑起来，但还不够适合作为长期方案，因为它会带来几个问题：

1. lexical score 和 vector score 尺度不一致  
   直接拼接后很难说清楚“为什么排成这样”。

2. vector query 返回的是 chunk 级结果  
   如果不先聚合成 news 级，最终来源里容易出现重复新闻。

3. 很难判断一条新闻是靠 lexical 命中的，还是靠 vector 命中的，还是两者都命中的。

所以后面又补了一步：

**把本地双路召回正式升级成 Local Hybrid Retrieval。**

### 这一阶段的核心思想

这一阶段不是简单做“两个 list 拼起来”，而是：

- 先把 vector chunk hits 聚合到 news 级
- 再用 rank 作为主信号
- 再叠加 lexical/raw、vector/raw、overlap、recency
- 对 lexical 和 vector 同时命中的新闻给额外 bonus

这本质上是一种：

**Weighted RRF 风格的本地融合**

虽然它还不是最终版本的 reranker，但已经比“简单拼接”更接近正式检索系统。

### 为什么这一步重要

因为这一步让你的项目可以更准确地表述成：

1. 先做 lexical baseline
2. 再接 Qdrant，让 vector retrieval 真正工作
3. 再把 lexical + vector 正式融合成本地 hybrid retrieval
4. 最后再继续往更完整的 rerank 和 LangGraph 工作流推进

这条路径比“后来我换成向量检索了”更完整，也更符合实际工程过程。

### 这一阶段还额外补了什么

为了让系统更可观察，还把每条来源的检索通道显式化了：

- `lexical`
- `vector`
- `lexical + vector`
- `web`

同时把 embedding 的配置模式也显式化了：

- `explicit`
- `llm-fallback`
- `partial`
- `missing`

这样系统不仅能检索，还能解释“当前检索到底是怎么工作的”。

## 第九阶段：把 Planner 落到执行层，补双路过滤与最终排序

在 `M3.9` 之后，系统虽然已经有：

- Retrieval Planner
- Local Hybrid Retrieval
- Web Search
- Final Grounded Answer

但这中间其实还缺一层关键控制：

- 不同检索计划下，到底该保留哪些证据
- 哪些弱相关结果应该被挡在最终回答之前
- 最终排序是不是已经真正体现了 `local-first / hybrid / web-first`

如果没有这一步，Planner 很容易只停留在“标签层”：

- 后端能说出当前是 `web-first`
- 但最终证据集未必真的更偏 Web

所以后面又补了一步：

**在 Planner 和回答之间，再加一层 Route-Aware Filtering + Final Rerank。**

### 这一阶段解决了什么

1. Planner 不再只是决定先查哪边  
   它还会影响：
   - 本地结果保留阈值
   - Web 结果保留阈值
   - 不同来源的数量配比

2. 最终排序不再只是“候选混在一起再排一遍”  
   现在会更明确地利用：
   - 当前检索计划
   - 本地 `lexical + vector` 双信号
   - 跨源互证
   - Web 域名和来源完整度

3. 运行时状态更完整  
   系统开始显式暴露：
   - `dualRouteFilterStrategy`
   - `finalRerankStrategy`

这意味着后面你在面试里不只可以讲：

- 我有 Planner

还可以继续讲：

- Planner 会真正影响后续过滤和排序

### 这一阶段的意义

这一步让系统第一次真正形成：

```text
Planner
-> Retrieval
-> Route-Aware Filtering
-> Final Rerank
-> Grounded Answer
```

这已经非常接近后续 LangGraph 节点化工作流的自然骨架。

所以你后面可以更完整地说：

1. 先做 lexical baseline
2. 再接 Qdrant，补本地向量召回
3. 再做 Local Hybrid Retrieval
4. 再把 Planner 落到执行层，用 filtering 和 rerank 真正控制最终证据集
5. 后面再继续升级为更完整的 LangGraph 工作流

## 第十阶段：补 Verifier、低置信度回退与无证据拒答

到 `M3.10` 为止，系统已经具备比较完整的受控检索工作流：

- Planner
- Retrieval
- Route-Aware Filtering
- Final Rerank
- Grounded Answer

但这还不够回答“如何控制幻觉”。

因为在新闻场景里，问题不只在于有没有检索到来源，还在于：

- 来源是不是太弱
- 来源是不是太少
- 模型是不是把弱证据写成了强结论

所以后面又补了一层：

**Verifier / Low-Confidence Fallback / No-Evidence Refusal**

这一层的意义是：

1. 不把真实性完全押在 prompt 上
2. 让系统对“证据强弱”有显式判定
3. 让回答在弱证据下自动降级成保守表达
4. 在无证据时明确拒答

这一步之后，你就可以把整条抗幻觉链路更完整地讲成：

```text
Retrieval Constraint
-> Prompt Constraint
-> Post-Generation Verifier
```

这比单纯说“我在 prompt 里要求模型不要幻觉”更有工程说服力。

同时，这一步也在为后面的 LangGraph 节点化工作流做准备，因为 `Verifier` 本身就很适合独立成一个工作流节点。

## 第十一阶段：把 Query Analysis 和 Response Formatter 从主链路里拆出来

到 `M3.11` 为止，系统已经有了比较完整的质量控制：

- Planner
- Retrieval
- Filtering
- Rerank
- Verifier

但如果继续往 Agent 工作流方向升级，还缺两个很重要的节点：

1. `Query Analysis`
2. `Response Formatter`

### 为什么要先拆 Query Analysis

一开始很多判断其实都混在 planner 里，比如：

- 这个问题更偏事实问答还是总结分析
- 时效性要求高不高
- 范围偏好更偏本地还是 Web

这些信息虽然最终会影响 planner，但它们本质上是：

**问题分析结果，而不是检索路线本身。**

所以后面补了一层 `Query Analysis`，先把：

- intent
- freshness need
- scope preference
- keyword hints

显式抽出来，再交给 planner。

这一步很重要，因为它让系统开始真正接近“节点化工作流”，而不是把所有逻辑都塞进 planner。

### 为什么要补 Response Formatter

系统即使已经能回答，也不代表输出已经“产品化”。

如果没有 formatter：

- 用户只能看到一段回答
- 很难感知系统对当前问题的分析
- 很难知道下一轮应该怎么追问

所以后面又补了一层 `Response Formatter`，负责：

- 规范化最终回复
- 生成 follow-up suggestions

这一步的价值不只是用户体验，更在于它把“最终输出”从“原样把模型文本吐出来”升级成了“有结构、有追问能力的 Agent 输出层”。

### 这一阶段之后，工作流怎么讲

这一步之后，你可以更完整地把系统讲成：

```text
Query Analysis
-> Retrieval Planner
-> Retrieval
-> Route-Aware Filtering
-> Final Rerank
-> Generator
-> Verifier
-> Response Formatter
```

## 第十三阶段：把主链路收口成 Stateful Workflow

到 `M3.12` 为止，系统逻辑上已经有很多节点了，但代码层面仍然比较像：

- 顺序调多个服务
- 最终拼一个 response

这虽然已经能跑，但和真正的工作流系统相比，还缺两样关键东西：

1. 统一的 workflow state
2. 可观察的 workflow trace

所以后面又补了一步：

**把当前主链路收口成 Stateful Workflow。**

### 为什么要先做这一步，而不是直接接 LangGraph

因为如果现在直接上 LangGraph，但内部状态和节点边界还不清晰，结果往往只是：

- 把现有函数硬包成 graph node
- 但节点语义、状态字段、轨迹信息依然混乱

所以更合理的顺序是：

1. 先把状态结构理顺
2. 先把节点轨迹显式化
3. 再考虑迁移到 LangGraph

### 这一步补了什么

这一阶段之后，系统已经具备：

- `WorkflowState`
- `workflowSummary`
- `workflowTrace`

并且 trace 已经覆盖：

- `query-analysis`
- `retrieval-planner`
- `retrieval`
- `route-filter`
- `final-rerank`
- `generator`
- `verifier`
- `response-formatter`

这意味着你现在不仅知道“最后回答了什么”，还知道：

- 每个节点是否执行
- 每个节点大致做了什么
- 某轮回答为什么会被 verifier 保护或回退

### 这一阶段的工程意义

这一步很重要，因为它让系统第一次真正具备：

```text
state
-> node
-> trace
```

这已经非常接近 LangGraph / LangSmith 风格的工作流系统了。

所以后面你在面试里可以更自然地讲：

“我没有直接为了用框架而用 LangGraph，而是先把现有主链路重构成 stateful workflow，把 query analysis、planner、retrieval、filter、rerank、generator、verifier、formatter 都显式拆成节点，并记录执行 trace。这样后面无论是接 LangGraph 还是接 LangSmith，都不是从零改造，而是在现有工作流骨架上继续演进。”

这比简单说“后面接 LangGraph”更扎实，因为你已经先把节点语义拆出来了。
## 第十四阶段：接入 LangSmith SDK Tracing

在上一阶段，我们已经有了：

- `state`
- `node`
- `trace`

但这些主要还是项目内部自定义的状态流和 trace。  
为了让工作流真正具备平台级观测能力，后面接入了 `LangSmith SDK tracing`。

### 为什么这一步重要

如果只有本地 trace，你可以知道系统做了什么，但不容易做到：

- 在官方平台里统一看每轮 run
- 对比不同问题、不同策略的链路差异
- 更方便地定位慢节点和失败节点

所以这一步的意义是把项目从“本地可观测”推进到“平台可观测”。

### 这一阶段之后，应该怎么讲

这时你可以说：

> 我先做了本地 run log 和 workflow trace，之后再接入 LangSmith 官方 SDK tracing，让工作流具备平台级观测能力。

---

## 第十五阶段：从 LangGraph 思想迁移到 StateGraph 语法

前面几个阶段里，项目已经非常接近 LangGraph 了：

- 有 `WorkflowState`
- 有明确节点
- 有条件分支
- 有 trace

但它仍然是“LangGraph 的思想”，不是“LangGraph 的官方语法”。

### 为什么这一步必须做

如果停留在思想层，你可以说“我参考了 LangGraph 设计工作流”，但很难进一步回答：

- `StateGraph` 怎么用
- 节点和边怎么声明
- `compile()` 之后怎么执行
- 为什么 LangSmith 图视图和官方文档里的表现不完全一致

所以这一步把工作流真正迁移到了 `StateGraph`：

```text
StateGraph
-> add_node
-> add_edge
-> conditional edge
-> compile
-> ainvoke
```

### 这一阶段之后，LangGraph 和 LangSmith 的关系

这时最准确的理解是：

- `LangGraph`：工作流运行时
- `LangSmith`：工作流观测与 tracing

也就是说，`LangGraph` 负责“怎么跑”，`LangSmith` 负责“怎么看”。

### 这一阶段之后，应该怎么讲

推荐表述：

> 我先把 Agent 主链路重构成 stateful workflow，等节点、状态和 trace 稳定后，再迁移到 LangGraph 官方 `StateGraph` 语法。这样 LangSmith 不仅能看到 trace，还更容易展示图结构和节点执行过程。

---

## 第十六阶段：导出工作流图并补评测基线

迁移到 `StateGraph` 之后，项目已经具备图结构了，但如果没有一个可直接导出的 graph 接口，你在项目文档、README 和面试里仍然很难快速展示：

- 有哪些节点
- 节点怎么连
- 哪些边是条件分支

所以这一阶段补了 `workflow graph export`，把图结构直接导出为：

- `nodes`
- `edges`
- `mermaid`

这样后面不依赖 Studio，也能直接展示工作流图。

### 为什么还要补评测基线

工作流图解决的是“结构可展示”，但面试里还会继续问：

- 你的 planner 准不准
- 你的 analysis 靠什么判断
- 你怎么验证这些启发式逻辑不是拍脑袋

所以这一阶段又补了一个**结构化评测基线**：

- 先不直接评测 LLM 文本质量
- 先评测 `plan / intent / freshness / scope`

这是一个更合理的工程顺序，因为检索前链路稳定，后面的 full-answer evaluation 才更有意义。

### 这一阶段之后，应该怎么讲

推荐表述：

> 当工作流迁移到 LangGraph StateGraph 之后，我又补了 graph export 和 evaluation baseline。前者把工作流节点和边直接导出成 Mermaid，方便文档展示；后者先验证 Query Analysis 和 Retrieval Planner 的准确性，让这套 Agent 不只是“能跑”，而且“有可验证的中间链路”。

---

## 第十七阶段：把评测变成反馈闭环

只有 baseline 还不够，因为面试官继续追问时，会更在意：

- 评测结果有没有被保存
- 失败 case 怎么沉淀
- 你有没有根据评测反向调优

所以这一阶段补了三件事：

1. `eval run` 自动落盘
2. `failure case` 自动沉淀
3. `LangSmith-ready dataset` 导出

### 为什么这一步重要

如果没有这一步，项目的评测更像：

- 跑一次接口
- 看一眼结果
- 然后就结束

而有了这一层之后，项目就变成：

```text
run eval
-> save result
-> inspect failures
-> tune heuristics
-> rerun eval
```

这就是比较完整的工程反馈闭环。

### 这一阶段的实际调优

通过 baseline 结果，发现：

- `进展` 被过度判成 `timeline`
- `最近` 被过度判成 `high freshness`

所以又对：

- `Query Analysis`
- `Retrieval Planner`

做了一轮基于失败 case 的 heuristic 调整。

这类优化非常适合在面试里讲，因为它说明：

- 你不是拍脑袋改规则
- 而是先有评测，再有反馈，再做迭代

### 这一阶段之后，应该怎么讲

推荐表述：

> 我没有把 evaluation 只做成一个单次接口，而是继续补成了 feedback loop。每次 baseline run 都会记录结果和 failure cases，再根据 mismatch 去调 Query Analysis 和 Planner。后续我还把评测集导出成 LangSmith-ready dataset，方便把本地 baseline 迁移到平台评测。 
