# M3.19 Response Evaluator And Verifier Casebook

## 本次做了什么

这一阶段补了两类收尾但非常重要的能力：

1. `Response-Level Evaluator`
2. `Verifier Casebook`

前面的 baseline 更偏“检索前链路评测”：

- Query Analysis
- Retrieval Planner
- freshness / scope / intent

这一阶段开始补“最终回答合同评测”，也就是：

- 回答有没有内容
- 是否带来源
- 是否带 workflow trace
- 是否带 follow-up suggestions
- `verificationStatus` 是否落在允许范围内

## 为什么要做 Response-Level Evaluator

如果只有 planner baseline，你能证明“前半段工作流比较稳定”，但还不能回答：

- 最终回答是不是结构完整
- guardrail 生效后，返回合同有没有被破坏
- accepted / guarded / refused 这三类输出在前端是否还能稳定消费

所以这一阶段补了一个更偏工程合同的 evaluator。

它不要求回答文本逐字匹配，因为新闻 Agent 的生成回答天然会有浮动。  
它重点检查的是：

- `status`
- `sources`
- `followUpSuggestions`
- `workflowTrace`
- `reply`

这类约束更适合新闻 Agent 的中后期评测。

## 为什么还要写 Verifier Casebook

`Verifier` 是新闻 Agent 里很关键的一层，但如果只写代码，没有一套“典型场景说明”，后面自己复习会很难。

所以这一阶段把 verifier 的典型 case 明确化，形成一个 casebook：

- 什么场景应 `accepted`
- 什么场景应 `guarded`
- 什么场景应 `refused`

这会直接帮助你后面回答：

- 为什么要做 verifier
- verifier 具体管什么
- verifier 和 retrieval / prompt 的边界是什么

## 技术含义

### 1. Response-Level Evaluator

它不是语义 judge，也不是让模型去给模型打分。  
它更像一层**回答合同检查器**。

它重点评测：

- `verificationStatus`
- `sourceCount`
- `followUpCount`
- `workflowTraceCount`
- `reply` 是否非空

### 2. Allowed Statuses

因为很多新闻问题本来就不适合“只能 accepted”。  
比如某些最新动态问题，即使系统返回 `guarded`，也可能是正确行为。

所以 response eval 用的是：

- `allowedStatuses`

而不是硬编码必须某一个状态。

### 3. Verifier Casebook

casebook 不是测试框架，而是一套“可复述的工程经验样例”。

它的价值在于：

- 便于复盘
- 便于文档展示
- 便于面试讲清楚 guardrail 思路

## 新增接口

- `GET /api/ai/eval/response/dataset`
- `POST /api/ai/eval/response/run`
- `GET /api/ai/eval/response/runs/recent`
- `GET /api/ai/eval/response/failures/recent`

## 如何测试

### 1. 看数据集

访问：

- `GET /api/ai/eval/response/dataset`

### 2. 跑 response eval

请求：

- `POST /api/ai/eval/response/run`

示例：

```json
{
  "limit": 3
}
```

### 3. 看最近 run

访问：

- `GET /api/ai/eval/response/runs/recent`

### 4. 看最近失败 case

访问：

- `GET /api/ai/eval/response/failures/recent`

## 面试怎么讲

推荐表述：

> 我把评测分成两层。第一层是 Query Analysis 和 Retrieval Planner 的结构化 baseline，用来评估中间链路；第二层是 Response-Level Evaluator，用来检查最终回答合同，例如 verificationStatus、sources、workflowTrace 和 follow-up 是否稳定。这让项目不只是在中间链路可解释，也在最终输出层可验证。
