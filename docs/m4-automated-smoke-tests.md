# M4 自动化冒烟测试

## 1. 这一轮做了什么

这一轮补的是最基础的一套自动化冒烟测试，而不是更重的单元测试框架。核心文件：

- [backend/tests/smoke_api.py](D:/Code/Fastapi/AgentNews/backend/tests/smoke_api.py)
- [.github/workflows/ci.yml](D:/Code/Fastapi/AgentNews/.github/workflows/ci.yml)

## 2. 为什么这样做

当前项目已经有很多能力：

- 新闻主链路
- AI 状态接口
- 工作流图导出
- planner baseline eval
- response-level eval

如果每次继续迭代都只靠手工点页面，很容易漏掉明显回归。  
但如果一开始就上很重的测试框架和大量 mock，成本也不划算。

所以这里先做的是：

- compile / build gate
- 关键接口 smoke check

## 3. smoke_api.py 做了什么

它会直接导入 FastAPI app，并用 `TestClient` 跑这些关键检查：

- `/`
- `/health`
- `/api/ai/status`
- `/api/ai/session/start`
- `/api/ai/session/{id}`
- `/api/ai/sessions`
- `/api/ai/workflow/graph`
- `/api/ai/eval/dataset`
- `/api/ai/eval/run`
- `/api/ai/eval/response/dataset`
- `/api/ai/eval/response/run`
- `/api/ai/session/{id}` 删除

这里会把更底层的聊天能力替换成一个 fake 响应，目的不是测试真实模型，而是验证：

- 路由是否还在
- schema 是否匹配
- 关键主链路是否没断

## 4. 为什么不在 CI 里直接跑真实 AI 对话

因为真实 AI 链路依赖：

- LLM key
- Tavily key
- 网络
- 有时还依赖本地数据库内容

这会让 CI 变得脆弱，也会让它失去“基础回归闸门”的价值。

## 5. 本地怎么跑

```powershell
cd D:\Code\Fastapi\AgentNews\backend
.venv\Scripts\python.exe tests\smoke_api.py
```

## 6. 这一层的意义

这一轮不是功能变多了，而是项目更像正式工程了。因为从这里开始，项目不仅有功能、有文档，也有最基本的自动化验证能力。
