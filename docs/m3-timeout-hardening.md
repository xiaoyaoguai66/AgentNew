# M3.4 补充：AI 链路超时治理与降级修复

## 问题背景

在 Tavily 接入之后，AI 链路从原来的：

- 本地检索
- 模型生成

扩展成了：

- 本地检索
- Tavily Web Search
- 双路融合 / rerank
- 模型生成

这时如果前端仍然沿用普通业务接口的统一超时配置，就会出现一个典型问题：

- AI 链路本身没有真正报错
- 但前端先因为超时而中断请求
- 用户看到的是 `timeout of 10000ms exceeded`

这说明问题不在“AI 助手不可用”，而在“超时策略不合理”。

## 根因分析

这次问题的根因一共有两层：

### 1. 前端把所有接口都设成了 10 秒超时

`frontend/src/api/http.js` 里之前统一使用：

- `timeout: 10000`

这个值对普通新闻列表、详情、收藏接口是够用的，但对 AI 链路不合适。  
因为 AI 请求天然比普通 CRUD 更慢，尤其是在 Tavily 开启之后，链路里多了一次外部搜索调用。

### 2. 后端 Tavily 超时过长，且会拖慢整条 AI 链路

后端原先 Tavily 请求使用的是固定 30 秒超时。  
如果外部搜索变慢，虽然最终可能还能返回，但前端已经在 10 秒时先超时了。

这会导致：

- 用户误以为整个 AI 功能崩了
- 实际上只是 Tavily 较慢
- 系统没有把“外部工具慢”正确降级为“仅本地检索”

## 这次为什么这样修

这次修复没有只做“把 10 秒改大”这么简单，而是做成了三层治理：

1. 前端 AI 请求使用独立超时  
   普通新闻接口仍保持轻量，AI 接口单独放宽时限。

2. 后端 Tavily 使用更短、更可控的超时  
   Web 搜索只是增强能力，不应该成为阻塞整个 AI 请求的关键路径。

3. 后端 Tavily 失败时自动降级  
   即使 Tavily 慢、超时或异常，也应尽量退回本地检索，而不是让整条链路直接失败。

## 实现原理

### 1. 前端：AI 接口单独超时

在 `frontend/src/api/ai.js` 中新增：

- `AI_STATUS_TIMEOUT_MS = 5000`
- `AI_CHAT_TIMEOUT_MS = 90000`

这样做的原因是：

- `/api/ai/status` 应该快，超时就直接失败即可
- `/api/ai/chat` 需要容纳检索 + 模型生成，不能沿用普通接口的 10 秒上限

### 2. 前端：统一错误提示更友好

在 `frontend/src/api/http.js` 中增加了超时错误识别：

- 如果是 axios 的 `ECONNABORTED`
- 或错误消息里包含 `timeout`

就显示统一的中文提示：

- `请求超时，请稍后重试`

这比直接把底层英文错误暴露给用户更合适。

### 3. 后端：Tavily 超时配置化

在配置中新增：

- `TAVILY_TIMEOUT_SECONDS`

并在 `backend/services/tavily_service.py` 中使用该配置，而不是写死 `30` 秒。

默认值现在是：

- `8` 秒

这样做的原因是：

- Tavily 是增强项，不是硬依赖
- 如果它在几秒内拿不到结果，继续等待的收益已经不高
- 更合理的策略是尽快降级到本地检索

### 4. 后端：Tavily 双重超时保护

为了避免线程调用被异常拖住，Tavily 现在有两层超时保护：

1. `urlopen(..., timeout=settings.tavily_timeout_seconds)`
2. `asyncio.wait_for(..., timeout=settings.tavily_timeout_seconds + 1)`

这能确保：

- Tavily 请求慢时尽快失败
- 不把整条 AI 链路卡太久

### 5. 后端：Tavily 失败自动降级

在 `news_agent_service.py` 中，双路检索现在通过：

- `asyncio.gather(..., return_exceptions=True)`

来收集结果。

策略是：

- 本地检索失败：直接抛错，因为这是主链路
- Web 检索失败：记录 warning，然后自动退回 `web_sources=[]`

也就是说，现在 Tavily 超时或异常时，系统仍然可以：

- 保留本地新闻检索
- 保留 grounded answer
- 只是不再提供 Web 来源

这比“整个请求直接报错”更符合企业级设计。

### 6. 后端：模型调用超时配置化

新增：

- `LLM_REQUEST_TIMEOUT_SECONDS`

并在 `backend/services/ai_service.py` 里使用该配置，而不是写死 `60` 秒。

当模型超时时，后端会明确返回：

- `504 Gateway Timeout`
- 中文错误信息说明是 AI 服务超时

## 这一步的意义

这次修复的意义，不只是“把超时 bug 修掉”，而是补齐了一类很重要的工程能力：

1. AI 链路和普通业务接口要有不同的超时策略
2. 外部增强工具必须 fail-open，而不是成为单点阻塞
3. 用户看到的报错应该是产品层错误，而不是底层英文异常
4. 超时配置应该可调整，而不是写死在代码里

## 手动测试

### 场景一：Tavily 正常

1. 在 `.env` 中配置 `TAVILY_API_KEY`
2. 正常启动前后端
3. 在 AI 页提问一个本地 + Web 都可能命中的问题，例如“卫星发射计划”
4. 页面不应在 10 秒内直接报 `timeout of 10000ms exceeded`
5. 如果 Tavily 正常命中，应返回本地来源与 Web 来源

### 场景二：Tavily 较慢或不可用

1. 保持 Tavily 开启
2. 模拟外部网络波动或错误 key
3. 再次提问
4. 系统应尽量降级回本地检索，而不是整个 AI 聊天直接失败

### 场景三：模型调用过慢

1. 如果模型服务本身很慢
2. 请求超过 `LLM_REQUEST_TIMEOUT_SECONDS`
3. 后端应返回明确的 AI 超时错误，而不是前端直接出现裸超时英文报错

## 配置项

这次新增了两个配置项：

- `LLM_REQUEST_TIMEOUT_SECONDS`
- `TAVILY_TIMEOUT_SECONDS`

模板文件 `.env.example` 已同步更新。

## 下一步

后续建议继续推进：

- 为不同工具源打点耗时日志
- 对 Tavily / 本地检索 / LLM 分别记录 latency
- 在 LangGraph 阶段把“工具超时 -> 降级分支”做成显式工作流节点
