# M3.17 Workflow Graph Export And Evaluation Baseline

## 本次做了什么

这一阶段补了两类能力：

1. `Workflow Graph Export`
2. `Evaluation Baseline`

前者解决“工作流图到底怎么展示”，后者解决“这套 query analysis / planner 怎么验证不是拍脑袋”。

新增接口：

- `GET /api/ai/workflow/graph`
- `GET /api/ai/eval/dataset`
- `POST /api/ai/eval/run`

## 为什么要做 Workflow Graph Export

你前面提到一个很关键的问题：

> 之前好像能在 studio 里看到图

这个记忆本身没有问题。  
只是要分清楚：

- `LangSmith` 更偏 tracing / evaluation / run 观察
- `LangGraph Studio` 或 graph 视图更偏 workflow 结构展示

为了让项目自己也能直接导出图结构，这一阶段我补了 `workflow graph export`。

现在后端会返回：

- `nodes`
- `edges`
- `mermaid`

这样就算不依赖 Studio，也可以：

- 在接口里直接看图结构
- 把 Mermaid 放进 GitHub README
- 在面试时明确展示节点和边

## 为什么要先做 Evaluation Baseline

当前新闻 Agent 已经有很多环节：

- Query Analysis
- Retrieval Planner
- Local / Web Retrieval
- Route Filter
- Final Rerank
- Verifier
- Formatter

但如果没有评测，你很难系统回答这些问题：

- Planner 分得准不准
- Query Analysis 的 intent 判断稳不稳
- freshness / scope 这些字段是不是合理

所以这一阶段先做了一个**结构化本地评测基线**，优先评测：

- `expectedPlan`
- `expectedIntent`
- `expectedFreshness`
- `expectedScope`

这是一种非常适合中期项目的做法，因为它：

- 不依赖大模型输出稳定性
- 不依赖联网结果波动
- 可以先验证检索前链路是否合理

也就是先把“前半段工作流”评稳，再继续做“完整问答效果评测”。

## 技术含义

### 1. Workflow Graph Export

它的作用是把工作流从“代码里的图”变成“可观察的图”。

当前会导出三种信息：

- `nodes`：节点列表
- `edges`：节点之间的边
- `mermaid`：可直接复制到 Markdown 的流程图文本

### 2. Evaluation Dataset

这不是训练集，而是**评测集**。  
也就是一组带预期标签的问题样本，用来检验系统行为。

当前评测集字段包括：

- `question`
- `mode`
- `timeRange`
- `category`
- `expectedPlan`
- `expectedIntent`
- `expectedFreshness`
- `expectedScope`

### 3. Evaluation Baseline

这里的 baseline 不是“最终模型能力”，而是“当前阶段最先要稳定的评测基线”。

因为如果 Query Analysis 和 Planner 本身就不稳定，后面再接：

- rerank
- verifier
- full answer evaluation

也会越来越难解释。

## 本次实现原理

### 1. Graph Export

如果当前引擎是 `langgraph`：

- 直接读取 `CompiledStateGraph`
- 拿到 graph 内部的 `nodes / edges`
- 再导出成 Mermaid

如果当前引擎是 `legacy`：

- 用静态节点定义补一份兼容图

所以这套接口既能支持现在的 `LangGraph`，也能兼容回退模式。

### 2. Evaluation Baseline

评测流程是：

```text
load eval dataset
-> run query analysis
-> run retrieval planner
-> compare with expected labels
-> compute planner / intent / freshness / scope accuracy
```

这一步还没有去评测：

- 最终回答文本是否完美
- Web 结果是否总是最优
- LLM 的生成质量

这是有意控制范围，因为这一阶段先要把**结构化工作流前半段**评稳。

## 如何测试

### 1. 工作流图

访问：

- `GET /api/ai/workflow/graph`

重点看：

- `engine`
- `style`
- `graphVisualizationReady`
- `nodes`
- `edges`
- `mermaid`

如果当前是 LangGraph 模式，预期：

- `engine = "langgraph"`
- `style = "langgraph-stategraph"`
- `graphVisualizationReady = true`

### 2. 评测集

访问：

- `GET /api/ai/eval/dataset`

应能看到内置测试样本。

### 3. 跑评测

请求：

- `POST /api/ai/eval/run`

示例 body：

```json
{
  "limit": 6
}
```

返回里重点看：

- `plannerAccuracy`
- `intentAccuracy`
- `freshnessAccuracy`
- `scopeAccuracy`
- `results`

## 面试怎么讲

推荐表述：

> 在工作流搭起来之后，我没有直接停在“能跑”，而是继续做了两件事。第一是把 LangGraph 工作流导出成结构化 graph 和 Mermaid，方便在项目文档和 GitHub 里展示节点与边；第二是先构建了一个结构化评测基线，优先验证 Query Analysis 和 Retrieval Planner 的行为是否符合预期。这样后面再做完整问答评测和 LangSmith evaluation 时，链路会更容易解释。
