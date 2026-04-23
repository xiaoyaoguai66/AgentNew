# AgentNews 最终交付清单

这份清单用于项目收尾、自测、上传 GitHub 和演示前的最后检查。

## 1. 环境配置

- 根目录 `.env` 已存在
- `MYSQL_URL` 已配置
- `REDIS_URL` 已配置
- `LLM_API_KEY` 已配置
- `TAVILY_API_KEY` 已配置
- `LANGSMITH_TRACING=true`
- `LANGSMITH_API_KEY` 已配置
- `LOCAL_RETRIEVAL_ENGINE=hybrid-ready`
- `ENABLE_VECTOR_RETRIEVAL=true`
- `EMBEDDING_BASE_URL / EMBEDDING_API_KEY / EMBEDDING_MODEL` 已配置

## 2. 本地运行检查

- 后端能启动
- 前端能启动
- `GET /health` 返回正常
- AI 页顶部状态显示正确：
  - 本地引擎
  - 向量
  - Embedding
  - Workflow
  - Verifier
  - Memory
  - LangSmith

## 3. 自动化校验

执行：

```powershell
cd D:\Code\Fastapi\AgentNews
powershell -ExecutionPolicy Bypass -File .\scripts\dev-check.ps1
```

预期：

- backend targeted compile checks 通过
- backend smoke checks 通过
- backend integration checks 通过
- frontend build 通过

## 4. 关键功能回归

- 新闻首页、分类切换、热门快读正常
- 新闻详情、相关推荐、阅读量正常
- 收藏、历史、“我的”页面正常
- AI 页本地问题可命中本地来源
- 最新问题可命中 Web 来源
- 来源卡片可跳转
- 会话侧栏可切换、恢复、删除历史会话
- LangSmith trace 可见
- `/api/ai/workflow/graph` 可导出图

## 5. 评测检查

- `POST /api/ai/eval/run` 可运行
- `POST /api/ai/eval/response/run` 可运行
- 最近评测记录可查看
- 最近失败样本可查看

## 6. GitHub 上传前检查

- `backend/data/qdrant/` 未提交
- `backend/data/agent_runs/` 未提交
- `backend/data/evals/*.jsonl` 未提交
- `.env` 未提交
- `.env.example` 不包含真实 key
- 没有无关调试文件、日志文件、IDE 目录

## 7. 演示材料检查

- [demo-script.md](D:/Code/Fastapi/AgentNews/docs/demo-script.md) 已过一遍
- [interview-storyline.md](D:/Code/Fastapi/AgentNews/docs/interview-storyline.md) 已过一遍
- [resume-project-experience.md](D:/Code/Fastapi/AgentNews/docs/resume-project-experience.md) 已准备好
- [interview-qa-cheatsheet.md](D:/Code/Fastapi/AgentNews/docs/interview-qa-cheatsheet.md) 已准备好
