# M3.12 Query Analysis 与 Response Formatter

## 这一阶段为什么要做

到 `M3.11` 为止，项目已经有：

- Retrieval Planner
- Local / Web Retrieval
- Route-Aware Filtering
- Final Rerank
- Verifier

这条链路已经能工作，但还存在两个结构性问题：

1. `Planner` 前面的判断还不够显式  
   很多关于“这个问题更偏事实问答还是总结分析”“时效性要求高不高”“范围更偏本地还是 Web”的判断，其实还混在 planner 里。

2. 最终回答虽然能返回，但“分析结果”和“继续追问建议”还没有被产品化  
   用户只能看到一段回复和来源卡片，不容易理解系统为什么这么查、下一轮还能怎么问。

所以这一阶段补的是两个节点：

- `Query Analysis`
- `Response Formatter`

目标是把当前受控工作流推进成：

```text
Query Analysis
-> Retrieval Planner
-> Retrieval
-> Filtering
-> Rerank
-> Generation
-> Verifier
-> Response Formatter
```

---

## 这一阶段做了什么

### 1. 新增 Query Analysis 节点

新增：

- `backend/services/query_analysis_service.py`

这一层会先对问题做启发式分析，当前输出包括：

- `intent`
- `freshnessNeed`
- `scopePreference`
- `keywordHints`
- `analysisReason`

当前的意图包括：

- `fact`
- `summary`
- `timeline`
- `compare`

时效性包括：

- `low`
- `medium`
- `high`

范围偏好包括：

- `local`
- `hybrid`
- `web`

也就是说，现在在进入 planner 之前，系统已经先得到了一份结构化的问题画像。

### 2. Retrieval Planner 改成基于 Query Analysis 决策

`retrieval_planner_service.py` 现在不再只盯着原始问题字符串，而是会参考 Query Analysis 的结果一起决策。

这一步的意义是：

- `Planner` 继续负责“决定走哪条检索路径”
- `Query Analysis` 负责“把问题特征显式抽出来”

这样后面如果你接 `LangGraph`，就很容易拆成两个独立节点，而不是把所有逻辑都糊在 planner 里。

### 3. Query Analysis 进入 Prompt

`ai_service.py` 和 `prompts/news_assistant.py` 现在会把 Query Analysis 结果写进最终 prompt。

这意味着模型拿到的不只是：

- 用户问题
- 对话历史
- 来源证据

还包括：

- 当前问题更偏什么意图
- 时效性需求强不强
- 范围偏好更偏本地还是 Web
- 关键词提示

这一步的作用不是让模型自己重新规划，而是让模型在“已经规划好的框架下”更稳定地组织回答。

### 4. 新增 Response Formatter

新增：

- `backend/services/response_formatter_service.py`

这一层现在负责两件事：

1. 规范化最终回答文本  
   比如合并多余空行、保证输出更稳定。

2. 生成追问建议  
   当前会根据：
   - 检索计划
   - 证据等级
   - 分类
   - 当前来源

   自动生成最多 3 条继续追问建议。

例如：

- “只看近24小时，再重新梳理一次这个问题”
- “只基于本地新闻库，重新总结一次”
- “把这件事对大模型行业的影响单独展开说一下”

### 5. 前端把 Query Analysis 和 Follow-Ups 展示出来

AI 页现在新增了两类展示：

1. 顶部状态
   - `Analysis Heuristic`
   - `Formatter Follow-Ups`

2. 每条回答内部
   - 问题分析结果
   - 继续追问建议按钮

用户现在可以直接点击追问建议，发起下一轮对话。

---

## 技术名词解释

### 1. Query Analysis

`Query Analysis` 指的是：

**在真正做检索之前，先对用户问题做结构化理解。**

它和 planner 的区别是：

- Query Analysis：抽取问题特征
- Planner：根据这些特征决定检索路线

### 2. Intent

这里的 `Intent` 不是复杂的意图分类模型，而是一个工程化任务类型标签。

当前分成：

- `fact`：事实问答
- `summary`：总结概览
- `timeline`：事件梳理
- `compare`：对比分析

这能帮助系统后面更稳定地：

- 决定回答结构
- 解释为什么走某种检索路径

### 3. Freshness Need

`Freshness Need` 指的是：

**这个问题对“最新信息”的依赖程度。**

例如：

- “今天最新的卫星发射计划” -> `high`
- “最近一周科技动态总结” -> `medium`
- “站内这篇新闻讲了什么” -> `low`

### 4. Response Formatter

`Response Formatter` 不是简单的“美化文本”，而是：

**在回答已经生成并校验完成后，再把结果整理成更稳定、更产品化的输出。**

当前它做的是：

- 文本规整
- 追问建议生成

后面还可以继续扩展成：

- 固定输出段落
- 引用区规范化
- follow-up 策略增强

---

## 为什么这一步重要

这一阶段的价值在于，它让系统开始具备“节点化工作流”的形态。

之前你可以讲：

```text
Planner -> Retrieval -> Answer
```

现在你可以更完整地讲：

```text
Query Analysis
-> Planner
-> Retrieval
-> Filter
-> Rerank
-> Generator
-> Verifier
-> Formatter
```

这对面试价值很高，因为它说明：

- 你不是只会接一个聊天接口
- 你在逐步把系统拆成可解释、可替换的节点
- 你知道哪一层负责理解问题，哪一层负责决策，哪一层负责结果质量控制

---

## 怎么测试

### 1. 看状态接口

访问：

- `GET /api/ai/status`

预期新增字段：

- `queryAnalysisEnabled = true`
- `queryAnalysisStrategy = heuristic-query-analysis`
- `responseFormatterEnabled = true`
- `responseFormatterStrategy = evidence-aware-followups`

AI 页顶部应看到：

- `Analysis Heuristic`
- `Formatter Follow-Ups`

### 2. 看回答内的问题分析

问 3 类问题：

1. `根据本地新闻库总结一下科技热点`
2. `今天最新的卫星发射计划有什么进展`
3. `最近科技新闻里哪些变化最可能影响大模型行业`

预期每条回答都能看到：

- 意图
- 时效
- 范围
- 分析说明

并且它们应该和问题本身的特征一致。

### 3. 看追问建议

每条回答下方应出现最多 3 条追问建议按钮。

测试方式：

- 点击任意建议
- 应能直接发起新一轮提问

### 4. 验证不同场景的建议是否变化

例如：

- 技术类问题更容易出现“大模型行业影响”
- 弱证据问题更容易出现“只看近24小时”“只基于本地新闻库”

这说明 formatter 不只是固定写死的模板，而是会根据当前证据状态变化。

---

## 和后续 LangGraph 的关系

这一步虽然还没有正式引入 LangGraph，但已经在结构上提前对齐了：

- `Query Analysis` 很适合变成一个独立节点
- `Response Formatter` 也很适合变成最终输出节点

因此后面如果你要把整条链路迁成 LangGraph，主要做的是：

- 把这些已有服务节点化
- 用图编排连接起来

而不是从零重写整个 Agent。
