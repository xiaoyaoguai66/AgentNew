# M3.18 Evaluation Feedback Loop

## 本次做了什么

这一阶段把“评测”从一次性的接口调用，推进成了一个可持续迭代的反馈闭环。

新增能力：

- 评测 run 自动落盘
- 失败 case 自动沉淀
- LangSmith evaluation-ready 导出
- 一轮基于 baseline 的 heuristic 调优

新增接口：

- `GET /api/ai/eval/runs/recent`
- `GET /api/ai/eval/failures/recent`
- `GET /api/ai/eval/langsmith/status`
- `GET /api/ai/eval/langsmith/export`
- `POST /api/ai/eval/langsmith/sync`

## 为什么要做这一阶段

前一阶段虽然已经有了 baseline，但还缺一个关键点：

> 评测结果有没有被沉淀下来，并反向驱动系统优化？

如果没有这一层，项目里即使有：

- `trace`
- `graph`
- `eval/run`

也仍然像“跑了一次 demo 评测”。

所以这一阶段补的不是新模型能力，而是一个真正的工程闭环：

```text
run eval
-> save run artifact
-> save failure cases
-> analyze mismatches
-> tune heuristics
-> rerun baseline
```

这比单纯展示 accuracy 更像真实项目迭代。

## 这次优化了什么

通过 baseline 结果，我发现两个最明显的问题：

1. `进展` 被过度判成 `timeline`
2. `最近` 被过度判成 `high freshness`

所以这次没有盲目继续加规则，而是按失败 case 反推 heuristic：

- `timeline` 触发词改得更保守
- `freshness` 改成优先看 `timeRange`，再看文本信号
- `planner` 不再因为 `summary` 就默认更偏 hybrid

优化后，baseline 从：

- `passedCount = 2/6`

提升到：

- `passedCount = 5/6`
- `plannerAccuracy = 0.8333`
- `intentAccuracy = 1.0`
- `freshnessAccuracy = 1.0`
- `scopeAccuracy = 1.0`

说明这一步已经不只是“跑评测”，而是完成了一次基于评测反馈的调优。

## 技术含义

### 1. Eval Artifact

就是把每次评测运行的摘要结果持久化下来。  
当前会记录：

- `runId`
- `recordedAt`
- `totalCount`
- `passedCount`
- `plannerAccuracy`
- `intentAccuracy`
- `freshnessAccuracy`
- `scopeAccuracy`

### 2. Failure Case

就是把每次评测中失败的样本单独沉淀下来。  
当前会记录：

- case 基本信息
- 实际结果
- 预期结果
- mismatch 列表

这样后面你可以直接按失败 case 去调 planner / analysis，而不是重新人工回忆问题。

### 3. LangSmith Evaluation-Ready

这一层不是直接替代本地 baseline，而是把本地评测集导出成更适合 LangSmith Dataset 的结构：

- `inputs`
- `outputs`
- `metadata`

这样后面你可以：

- 继续在本地跑 baseline
- 或者把数据集同步到 LangSmith 平台做更正式的评测实验

## 本次实现原理

### 1. 评测结果自动落盘

每次调用 `POST /api/ai/eval/run` 时：

- 先生成 `runId`
- 执行 baseline
- 把 run 摘要写入 `eval_runs.jsonl`
- 把失败 case 写入 `eval_failures.jsonl`

### 2. LangSmith 导出

LangSmith 导出当前不直接依赖模型输出，而是先导出：

- 问题输入
- 期望的 plan / intent / freshness / scope
- case metadata

这是一个很适合中期项目的评测数据形态，因为稳定、可解释，也方便后面扩展。

## 如何测试

### 1. 先跑 baseline

请求：

- `POST /api/ai/eval/run`

示例：

```json
{
  "limit": 6
}
```

### 2. 查看最近 run

访问：

- `GET /api/ai/eval/runs/recent`

### 3. 查看最近失败 case

访问：

- `GET /api/ai/eval/failures/recent`

### 4. 查看 LangSmith evaluation 状态

访问：

- `GET /api/ai/eval/langsmith/status`

### 5. 导出 LangSmith dataset payload

访问：

- `GET /api/ai/eval/langsmith/export`

### 6. 同步到 LangSmith

请求：

- `POST /api/ai/eval/langsmith/sync`

如果当前 LangSmith 未配置，系统会安全返回“仅支持本地导出”；如果已配置，则会尝试创建 dataset 并上传 examples。

## 面试怎么讲

推荐表述：

> 我不仅做了 LangGraph 工作流和 LangSmith tracing，还补了一个 evaluation feedback loop。具体做法是先构建结构化 baseline，自动记录每次评测 run 和失败 case，再根据 mismatch 反推 Query Analysis 与 Retrieval Planner 的 heuristic 调优。后续还把这组评测数据导出成 LangSmith-ready dataset，方便继续做平台化评测和实验。
