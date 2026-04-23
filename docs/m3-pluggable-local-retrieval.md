# M3.6 可插拔本地检索层：为 Qdrant 接入做准备

## 这一阶段为什么要做

到 `M3.5` 为止，新闻助手已经具备：

- `Retrieval Planner`
- 本地新闻 lexical baseline
- Tavily Web Search
- Query Rewrite
- Fusion + 轻量 rerank

但本地检索层还有一个明显问题：

**当前本地检索只有一套实现，而且入口和实现是绑定在一起的。**

这会带来两个后续问题：

1. 一旦接 `Qdrant`，就要直接改写现有本地检索主链路  
   这会让 `M3.3 ~ M3.5` 里已经稳定下来的 Planner、Fusion 和 AI 主流程重新承受改动风险。

2. 面试时很难把“方法演进”讲清楚  
   如果代码里只有一个 `news_retrieval_service.py`，很难清晰说明：
   - 当前用的是 lexical baseline
   - 后面准备怎么接向量检索
   - 为什么要先做 abstraction 再上 Qdrant

所以 `M3.6` 的目标不是立刻把向量检索全做完，而是：

**先把本地检索做成可插拔结构，让 lexical baseline 和后续 Qdrant 集成有稳定接口。**

---

## 这一阶段解决了什么

本次改造后，本地检索层从“单文件实现”升级成了三层结构：

1. `lexical_news_retriever.py`
   - 保留并承接当前可运行的 lexical baseline

2. `vector_news_retriever.py`
   - 作为 Qdrant / vector retrieval 的预留实现入口

3. `news_retrieval_service.py`
   - 作为统一的本地检索 façade
   - 由它决定当前使用哪种本地引擎

这样做以后：

- Agent 主链路只依赖 `news_retrieval_service.retrieve_news_sources()`
- 具体是 lexical 还是后续 vector，不会再泄漏到更上层
- 后面接 Qdrant 时，主要改动会被限制在本地检索层内部

---

## 本次代码结构变化

新增：

- `backend/services/lexical_news_retriever.py`
- `backend/services/vector_news_retriever.py`

重构：

- `backend/services/news_retrieval_service.py`

其中职责划分如下：

### 1. lexical_news_retriever.py

这里承接了你当前已经验证过的本地检索 baseline：

- MySQL 候选集
- 类别过滤
- 时间范围过滤
- lexical 打分
- snippet 抽取

也就是说：

**当前真正跑在线上的本地检索，仍然是这条 lexical baseline。**

这能保证：

- 当前功能不回退
- 之前的调优逻辑不丢
- 本地 grounded QA 仍然保持稳定

### 2. vector_news_retriever.py

这一层现在的定位不是“已经完成向量检索”，而是：

**预留统一的 vector retrieval 接口，并把运行时状态显式化。**

当前它会输出：

- `vectorRetrievalEnabled`
- `vectorStoreConfigured`
- `vectorBackend`
- `vectorRetrievalActive`

而真正的向量召回逻辑暂时还没有接入，原因很明确：

- 还没有新闻 chunk embedding 流程
- 还没有向量索引构建流程
- 还没有正式的 Qdrant 查询链路

所以这一层目前是“vector-ready”，不是“vector-complete”。

这也是这一步设计上最重要的地方：

**先把接口和状态边界搭好，再把真正的向量检索填进去。**

### 3. news_retrieval_service.py

这一层现在变成了本地检索总入口。

它负责：

- 解析当前本地检索引擎配置
- 统一输出本地检索运行时状态
- 默认走 lexical baseline
- 在 `hybrid-ready` 模式下，为后续向量检索融合预留路径

当前支持的本地引擎配置：

- `LOCAL_RETRIEVAL_ENGINE=lexical`
- `LOCAL_RETRIEVAL_ENGINE=hybrid-ready`

含义是：

- `lexical`
  - 只用当前已稳定的 lexical baseline

- `hybrid-ready`
  - 保持 lexical 可用
  - 同时打开“未来可以并入 vector sources”的代码结构

---

## 为什么这一步不直接把 Qdrant 全接完

原因不是“不能做”，而是“现在这样更合理”。

Qdrant 真正接入至少还需要补齐下面几层：

1. 新闻切 chunk
2. embedding 生成
3. 建索引 / upsert
4. metadata 设计
5. 查询接口
6. 向量召回结果和当前 lexical 结果的本地融合

如果这些还没准备好，就直接把 Qdrant 强接进当前主链路，会出现两个问题：

- 代码里会充满半成品逻辑
- 面试时也很难说清楚“当前到底接到了哪一步”

因此这一步的工程策略是：

**先把结构抽象到位，再让 Qdrant 真正接入。**

这比把一个“还没建立 embedding/index pipeline”的向量库硬塞进主流程更稳。

---

## 配置层也一起准备好了

这次还把后续 Qdrant 和 embedding 相关配置补进了：

- `LOCAL_RETRIEVAL_ENGINE`
- `ENABLE_VECTOR_RETRIEVAL`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION`
- `QDRANT_TIMEOUT_SECONDS`
- `EMBEDDING_BASE_URL`
- `EMBEDDING_API_KEY`
- `EMBEDDING_MODEL`

这些配置现在已经进入：

- `backend/config/settings.py`
- `.env.example`

意义在于：

1. 后面接 Qdrant 时不需要再重构配置系统
2. 运行时状态能够明确知道：
   - 有没有打开向量检索开关
   - Qdrant 是否已配置
   - 当前是不是只是 `reserved / ready` 状态

---

## 前端为什么也要显示这些状态

这次我还把运行时状态透到了 `/api/ai/status`，并在 AI 页加了两个新状态：

- `本地引擎`
- `向量`

这件事看起来像“调试 UI”，但其实对项目很重要。

原因是：

1. 你自己调试时能立刻看到当前是不是还在 lexical baseline
2. 后面接 Qdrant 后，页面上能直接体现“当前已经切到了 vector-ready / vector-active”
3. 面试时可以直接展示：这个系统不是静态写死，而是能观察当前检索栈状态

---

## 这一步在方法演进里的意义

这一步非常适合你后面在面试里解释：

“我没有在 lexical baseline 还没稳定的时候就直接强上向量库，而是先把本地检索层做成可插拔结构。这样当前系统继续稳定运行，后续接 Qdrant 只需要在 retriever 层内部补 chunk、embedding 和向量查询，不需要把 Planner、Fusion 和 grounded answer 全部重写。” 

这句话的价值很高，因为它体现的是：

- 结构演进意识
- 可维护性意识
- 对中间态方案的工程控制

---

## 当前状态要说准确

这一阶段完成后，最准确的描述是：

- 当前线上本地检索引擎：`lexical baseline`
- 当前系统结构：`vector-ready`
- 当前向量检索状态：`接口和配置已预留，但 Qdrant + embedding pipeline 还没正式接入`

不要把这一步说成“已经完成了向量检索”，那样会在面试里被问穿。

正确说法应该是：

**“我先把本地检索层做成了可插拔架构，保持 lexical baseline 持续可用，同时为 Qdrant 接入预留了独立 vector retriever 和运行时配置。”**

---

## 手动测试建议

你现在可以这样验证这一阶段：

1. 正常启动前后端
2. 打开 AI 页
3. 查看顶部状态：
   - `本地引擎` 默认应显示 `lexical-baseline`
   - `向量` 默认应显示 `未开启`
4. 如果你在 `.env` 里设置：
   - `LOCAL_RETRIEVAL_ENGINE=hybrid-ready`
   - `ENABLE_VECTOR_RETRIEVAL=true`
   - 但不配置 `QDRANT_URL`
   那前端应显示：
   - `本地引擎` 变成 `lexical-plus-vector-ready`
   - `向量` 变成 `开关已开，索引未配`
5. 在这两种模式下继续提问，当前回答能力不应回退，因为 lexical baseline 仍然是默认主链路

---

## 下一步怎么接 Qdrant

有了这一层 abstraction，下一步就可以正式推进：

1. 新闻 chunk 设计
2. embedding 生成链路
3. Qdrant upsert / 索引初始化
4. metadata filter
5. vector retrieval 和 lexical retrieval 的本地混合召回

也就是说，从这一阶段开始，后续的 Qdrant 接入终于能变成：

**在稳定接口里填实现，而不是推翻现有结构。**
