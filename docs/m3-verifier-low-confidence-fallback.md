# M3.11 Verifier、低置信度回退与无证据拒答

## 这一阶段为什么要做

到 `M3.10` 为止，项目已经具备：

- Retrieval Planner
- 本地 hybrid retrieval
- Tavily Web Search
- Route-Aware Filtering
- Final Rerank
- Grounded Answer

但这还不等于“回答已经足够稳”。

新闻问答里最容易出问题的地方，不一定发生在检索阶段，也可能发生在：

1. 检索到了来源，但来源偏弱，模型却写得过于肯定
2. 来源数量不多，模型给出了一段看起来很完整的结论
3. 回答没有明确引用，用户很难分辨哪些是证据，哪些是模型组织语言后的推断

所以这一阶段补的不是新的检索能力，而是：

**在模型生成之后、返回给前端之前，再加一层受控校验。**

这一步的目标很明确：

- 证据不足时，不让模型硬编
- 低置信度时，自动切成保守回答
- 无证据时，直接拒答

---

## 这一阶段做了什么

### 1. 新增后置校验服务

新增：

- `backend/services/answer_verifier_service.py`

这一层是一个 rule-based verifier，放在：

```text
Planner
-> Retrieval
-> Filtering
-> Final Rerank
-> LLM Generation
-> Verifier
-> Response Formatter
```

它不替代检索，也不替代 prompt，而是在最终返回前再做一次守门。

### 2. 对回答结果做三类判定

当前 verifier 会把结果分成：

- `accepted`
- `guarded`
- `refused`

含义分别是：

- `accepted`
  说明当前回答通过了后置校验，可以按原样返回。

- `guarded`
  说明当前回答虽然不是完全无证据，但证据偏弱、置信度偏低，或者表达过于肯定，所以系统会自动加上保守说明，降低误导风险。

- `refused`
  说明当前证据不足，不应该继续生成确定性结论，所以直接拒答。

### 3. 新增低置信度回退

如果满足下面这类情况，系统会触发 `guarded`：

- 当前 `confidence` 低于低置信度阈值
- 只有 1 条来源
- 只有 1 条弱 Web 来源
- 证据等级是 `weak`
- 回答里出现明显过度肯定的表达

这时系统不会直接丢弃回答，而是：

- 保留已有回答主体
- 在前面加上“当前证据支撑偏弱，应视为保守判断”
- 在后面提示用户继续缩小时间范围、切换主题或限定来源

这一步的意义是：

**不把所有低质量回答都粗暴拒掉，而是把它降级成更安全的表达。**

### 4. 新增无证据拒答

如果最终来源为空，系统会直接返回：

- `verificationStatus = refused`
- `evidenceLevel = none`
- `guardrailApplied = true`

同时给出“当前证据不足，建议换关键词或缩小范围再问”的拒答文案。

这一步和之前的“no-hit fallback”不一样，区别在于：

- 之前更像 retrieval fallback
- 现在它被纳入统一的 verifier 语义中

也就是说，后面你讲项目时可以明确说：

**系统对无证据场景做了显式拒答，而不是简单返回一句模糊错误信息。**

### 5. 前后端都透出了校验状态

后端新增返回字段：

- `verificationStatus`
- `verificationReason`
- `evidenceLevel`
- `guardrailApplied`

前端 AI 页现在会显示：

- `Verifier Rule-Based`
- 每条回答的校验状态
- 每条回答的证据等级
- 是否触发了保护

这让系统从“内部做了校验”变成“用户也能感知校验”。

---

## 技术名词解释

### 1. Verifier

这里的 `Verifier` 不是另一个大模型，也不是复杂的 agent。

当前项目里的 verifier 指的是：

**在回答生成完成之后，用一组规则再次检查这条回答是否适合直接给用户。**

它属于典型的 post-generation guardrail。

### 2. Low-Confidence Fallback

`Low-Confidence Fallback` 的意思是：

当系统判断这次回答证据偏弱、置信度偏低时，不直接当作稳定结论输出，而是自动切成保守表达。

这和“重试一次”不一样，也和“直接报错”不一样。

它本质上是在做：

**回答风格降级。**

### 3. No-Evidence Refusal

`No-Evidence Refusal` 的意思是：

当没有足够证据时，系统明确拒绝给出确定结论。

它和“我暂时不知道”相比更工程化，因为它是：

- 显式判定
- 可观测状态
- 有固定触发条件

### 4. Evidence Level

当前把证据等级分成：

- `none`
- `weak`
- `moderate`
- `strong`

它不是一个单独模型预测出来的值，而是综合：

- 来源数量
- 来源类型多样性
- 本地是否同时被 lexical 和 vector 命中
- 最终 confidence

推出来的工程化等级。

---

## 为什么这一步不能只靠 Prompt

很多项目会把“抗幻觉”完全寄托在 system prompt 上，但这有两个问题：

1. Prompt 只能约束模型倾向，不能保证每次都完全执行
2. Prompt 很难直接感知“这次来源是不是太弱”“这次是否只命中了一条 Web 结果”

所以这一步保留了 prompt 约束，但又补了一层 verifier。

也就是说，现在的抗幻觉链路是：

```text
检索约束
-> Prompt 约束
-> 后置 Verifier 校验
```

这比只说“我在 prompt 里要求模型不要幻觉”要扎实得多。

---

## 这一阶段的工程价值

这一步非常适合你后面面试时这样讲：

“我没有把真实性控制只交给 prompt，而是加了一层 post-generation verifier。这样系统在检索到的证据偏弱时，会自动降级成保守回答；如果没有足够证据，则明确拒答。这样就把新闻问答里的 grounded generation、低置信度回退和无证据拒答串成了一条完整的 guardrail 链路。”

这段话的价值在于它说明：

- 你知道 prompt 不是万能的
- 你知道生成式系统需要 guardrail
- 你把 guardrail 落到了代码结构里

---

## 怎么测试

### 1. 看状态接口

访问：

- `GET /api/ai/status`

预期新增字段：

- `verifierEnabled = true`
- `verifierStrategy = rule-based-post-verifier`

前端 AI 页顶部也应出现：

- `Verifier Rule-Based`

### 2. 测无证据拒答

输入一个本地和 Web 都很难命中的问题，预期：

- `verificationStatus = refused`
- `evidenceLevel = none`
- `guardrailApplied = true`

同时回答会明确告诉你当前证据不足。

### 3. 测低置信度回退

输入一个命中来源较少、但又不是完全无来源的问题，预期：

- `verificationStatus = guarded`
- `evidenceLevel = weak`
- `guardrailApplied = true`

回答前面会多出保守判断说明。

### 4. 测正常通过

输入一个本地和 Web 都命中良好的问题，预期：

- `verificationStatus = accepted`
- `guardrailApplied = false`

说明当前回答通过了后置校验，没有被回退。

---

## 和后续 LangGraph 的关系

这一步虽然还是规则校验，但它非常适合后面迁移成工作流节点：

- `Retriever`
- `Filter`
- `Rerank`
- `Generator`
- `Verifier`

也就是说，`M3.11` 虽然没有直接接 LangGraph，但已经提前把一个很关键的节点拆出来了。

这让后面工作流升级不需要推翻现有代码结构，只需要把当前 verifier 节点化即可。
