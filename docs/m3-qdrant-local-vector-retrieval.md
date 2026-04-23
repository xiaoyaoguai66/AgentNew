# M3.8 Qdrant 本地向量检索：把 vector-ready 变成真正可用的本地召回

## 这一阶段做了什么

这一阶段把 `M3.6` 和 `M3.7` 里已经预留好的向量检索结构，真正补成了可运行链路：

1. 安装并接入 `qdrant-client`
2. 让后端支持 `Qdrant local persistent mode`
3. 打通 `新闻切块 -> embedding -> collection -> upsert -> query` 全流程
4. 让 `vector_news_retriever` 不再只是预留接口，而是能返回真实向量召回结果
5. 保持现有 lexical baseline 继续可用，并在 `hybrid-ready` 模式下和向量结果融合

也就是说，到这一阶段为止，项目里的本地检索已经不再只是：

- lexical baseline

而是升级成了：

- lexical baseline
- Qdrant 本地向量召回
- 两者可插拔、可融合

---

## 为什么这一步这样做

### 1. 为什么不是直接上 Docker 版 Qdrant

理想情况下，企业环境通常会把 Qdrant 作为独立服务运行。

但当前本地环境里，Docker daemon 不可用，所以这一步没有强行要求先把容器链路跑通，而是选择了 `qdrant-client` 自带的本地持久化模式。

这样做的原因很现实：

1. 先把“向量检索主能力”跑通
2. 避免被本地 Docker 环境卡住整条研发路径
3. 后续如果需要切到独立 Qdrant 服务，只需要改配置，不需要推翻当前检索结构

所以这一步的工程策略是：

**先用 Qdrant local mode 跑通真实向量检索，再保留后续切到服务化部署的空间。**

### 2. 为什么不是按新闻类别选不同 embedding

当前没有按“科技 / 财经 / 国际”分别选不同 embedding 模型，而是坚持一套统一的 retrieval embedding。

原因是：

1. 检索时，`query` 和 `document chunk` 必须在同一个向量空间里比较
2. 新闻分类过滤更适合交给 metadata filter，而不是拆成多套 embedding 模型
3. 多模型会让索引维护、召回对齐和面试解释都变复杂

所以当前更合理的方案是：

- 一套统一 embedding
- `category / publish_time / source` 这些信息走 payload filter
- 最终排序再结合 lexical / rerank 处理

### 3. 为什么这一阶段保留 lexical baseline

因为向量检索不是来“替换所有东西”的，而是来补 lexical retrieval 的短板。

新闻场景里：

- `lexical retrieval` 擅长命中实体词、标题词、政策名、公司名
- `vector retrieval` 擅长语义相近、表达改写、模糊提问

所以更适合新闻项目的，不是“只保留一个”，而是：

**lexical + vector 的混合检索。**

---

## 这一步涉及的技术名词是什么意思

### 1. Chunk

`chunk` 就是把一篇完整新闻拆成多段后，每一段形成的最小检索单元。

为什么要拆：

- 一整篇新闻直接做向量，粒度太粗
- 用户问题通常只对应正文里的某一部分
- chunk 还能方便后续做来源引用和 snippet 展示

当前项目里，新闻切块策略是：

- 标题和摘要增强
- 段落优先
- 固定字符窗口
- overlap 防止边界信息被切断

### 2. Embedding

`embedding` 可以理解成“把文本变成一串高维数字向量”，这样系统就能比较两段文本在语义上的接近程度。

这一步做的不是分类，而是为了检索：

- 用户问题先转成向量
- 新闻 chunk 也转成向量
- 再在向量库里找“最接近”的 chunk

### 3. Collection

`collection` 是 Qdrant 里的“向量集合”。

你可以把它理解成：

- 一个专门存新闻 chunk 向量的表
- 但它不只存向量，也存每个点的元数据

当前默认 collection 是：

- `agentnews_news_chunks`

### 4. Payload

`payload` 就是跟着向量一起存进去的元数据。

当前项目里主要包括：

- `news_id`
- `chunk_id`
- `chunk_index`
- `title`
- `snippet`
- `chunk_text`
- `category_id`
- `publish_time`
- `publish_timestamp`
- `author`

这些字段很重要，因为后面检索不只是“相似度最高”，还要支持：

- 分类过滤
- 时间范围过滤
- 来源展示
- 点击来源跳新闻详情

### 5. Local Persistent Mode

这是这一步专门选用的 Qdrant 运行方式。

它的含义是：

- Qdrant 不单独起一个远程服务
- 而是把索引直接持久化到本地目录
- 当前目录默认是 `backend/data/qdrant`

优点：

- 本地开发简单
- 不需要先配服务端
- 真实可持久化，不是纯内存 demo

限制：

- 同一份本地目录一次只能被一个 Qdrant client 实例占用
- 更适合单机开发，不是最终生产部署方式

---

## 本次代码改动的核心点

### 1. 安装依赖并写回 requirements

本次新增依赖：

- `qdrant-client==1.17.1`

这样别人拉你的项目后，只要按 `requirements.txt` 安装，就能复现这一步。

### 2. Qdrant 客户端改成真实实现

`backend/services/qdrant_index_service.py` 现在不再是占位实现，而是支持：

- 本地模式或服务模式自动切换
- collection 是否存在检查
- collection 初始化
- payload 组装
- point upsert
- 向量查询
- category / publish_time 过滤

### 3. Embedding 服务支持 DashScope 兜底

`backend/services/embedding_service.py` 现在支持：

- 如果显式配置了 `EMBEDDING_*`，优先用独立 embedding 配置
- 如果没有单独配置，但 `LLM_BASE_URL` 是 DashScope 兼容模式地址，就自动回退到：
  - `https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings`
  - `text-embedding-v4`
  - `LLM_API_KEY`

这样做的好处是：

- 你当前项目已经有 DashScope 的模型接入
- 不需要为了第一版向量检索再额外改很多环境变量
- 先把本地向量召回跑通

### 3.1 为什么建议后面再补显式 `EMBEDDING_*`

这一阶段为了先跑通能力，允许了 `LLM -> Embedding` 的回退模式。

但从工程清晰度和面试表达来说，后续更推荐显式写出：

```env
EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings
EMBEDDING_API_KEY=你的_key
EMBEDDING_MODEL=text-embedding-v4
```

这样做的好处是：

1. 配置职责更清楚  
   聊天模型和 embedding 模型是两条能力，不再混在一起。

2. 后续切换 provider 更方便  
   如果以后不用 DashScope，也不需要再改 LLM 相关配置。

3. 面试更好解释  
   可以直接说：`LLM` 负责生成，`Embedding` 负责检索，配置是独立的。

当前系统里，运行时状态也会明确区分：

- `explicit`
- `llm-fallback`
- `partial`
- `missing`

这样你在 AI 页里能直接看到当前 embedding 到底是显式配置，还是沿用聊天模型配置回退出来的。

### 4. 向量检索从 placeholder 变成真实召回

`backend/services/vector_news_retriever.py` 现在会真正执行：

1. 把用户问题 embedding 化
2. 根据 category 和 timeRange 计算 filter
3. 去 Qdrant 查询 top-k
4. 把返回点映射成 `AiSourceItem`

这意味着：

**当前系统里的 `vector-ready` 已经正式升级成了 `vector-active`。**

### 5. 本地检索状态变成可观察

`news_retrieval_service.py` 现在会明确区分：

- `lexical-baseline`
- `lexical-plus-vector-ready`
- `lexical-plus-qdrant`

这样你在 AI 页就能直接看到当前本地检索到底跑在哪一层。

### 6. 关闭应用时主动释放本地 Qdrant 文件锁

因为当前使用的是本地持久化目录，所以这一步还补了：

- FastAPI 关闭时主动 `close_client()`

这样下一次重启后端时，更不容易遇到本地索引目录被占用的问题。

---

## 当前向量检索链路怎么工作

现在本地向量检索的真实流程是：

```text
新闻正文
-> chunking
-> embedding
-> Qdrant collection upsert

用户问题
-> query embedding
-> Qdrant query
-> payload 映射为来源
-> 和 lexical results 融合
-> grounded answer
```

其中当前融合策略仍然保持保守：

- lexical baseline 继续保留
- vector 作为补充召回源
- 不会因为接入向量检索就让原有稳定链路回退

---

## 这一步的验证结果

本次已经实际验证过：

1. `qdrant-client` 已安装到后端虚拟环境
2. 本地 Qdrant 状态可正常返回
3. embedding 状态可正常返回
4. `preview` 能看到真实 chunk
5. `sync` 的 `dry-run` 可正常返回
6. 真实索引同步可把新闻 chunk 写入 Qdrant
7. 再用同一条新闻标题提问时，向量召回能返回对应来源

也就是说，这一步不是“接口预留”，而是已经完成了真实的本地向量召回闭环。

---

## 手动测试建议

### 1. 环境变量

在根目录 `.env` 中至少保证：

```env
LOCAL_RETRIEVAL_ENGINE=hybrid-ready
ENABLE_VECTOR_RETRIEVAL=true
QDRANT_URL=
QDRANT_LOCAL_PATH=backend/data/qdrant
```

如果你不单独配 embedding，也可以沿用当前 DashScope：

```env
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
LLM_API_KEY=你的key
EMBEDDING_BASE_URL=
EMBEDDING_API_KEY=
EMBEDDING_MODEL=
```

如果你想把配置写得更完整，推荐直接改成：

```env
LOCAL_RETRIEVAL_ENGINE=hybrid-ready
ENABLE_VECTOR_RETRIEVAL=true

QDRANT_URL=
QDRANT_LOCAL_PATH=backend/data/qdrant
QDRANT_COLLECTION=agentnews_news_chunks
QDRANT_TIMEOUT_SECONDS=5

EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings
EMBEDDING_API_KEY=你的_key
EMBEDDING_MODEL=text-embedding-v4
```

### 2. 看状态

启动后端后，先看：

- `GET /api/ai/status`
- `GET /api/ai/index/status`

预期：

- `localRetrievalLabel = lexical-plus-qdrant`
- `vectorRetrievalActive = true`
- `indexSyncReady = true`

### 3. 看切块

调用：

- `GET /api/ai/index/preview/1`

预期：

- 能看到新闻 1 被切成几个 chunk
- 每个 chunk 有 `snippet / text / charCount`

### 4. 跑一次 dry-run

调用：

- `POST /api/ai/index/sync`

请求体：

```json
{
  "dryRun": true,
  "limit": 5
}
```

预期：

- 看到准备同步多少条新闻、多少个 chunk
- 不真正写入 Qdrant

### 5. 做一次真实同步

仍然调用：

- `POST /api/ai/index/sync`

请求体：

```json
{
  "dryRun": false,
  "newsIds": [1]
}
```

预期：

- 返回 `status = synced`
- 有 `upsertedPoints`
- 有 `vectorSize`

### 6. 验证向量召回

同步后，去 AI 页问一条和已同步新闻相近的问题。

例如：

- 直接用这条新闻标题
- 或者换一种更语义化的表达方式

预期：

- 来源能命中这条本地新闻
- 当前本地引擎状态显示为 `lexical-plus-qdrant`

---

## 这一阶段在方法演进里的意义

这一步很适合你后面在面试里解释成：

“我没有在一开始就把系统完全建立在向量检索上，而是先做了 lexical baseline，确保 grounded QA 和来源约束先成立。后续再把本地检索层抽象出来，最后接入 Qdrant 做真实向量召回。这样系统是沿着可解释 baseline -> 可插拔结构 -> 真实向量检索的顺序演进，而不是一上来堆很多基础设施。” 

这条演进路径的价值在于：

- 方法试错过程清楚
- 每一步为什么做都讲得通
- 代码结构和工程节奏是匹配的

---

## 下一步

`M3.8` 完成后，下一步更自然的方向是：

1. 把当前本地向量召回进一步接入更正式的 hybrid retrieval
2. 增加更细的 payload filter 和 rerank
3. 继续朝 `LangGraph` 风格工作流推进

也就是说，这一步完成后，项目已经从“准备接向量检索”进入了“已经具备真实向量检索能力”的阶段。
