# M4 CI 与交付层加固

## 1. 这一轮做了什么

这一轮没有继续叠 Agent 功能，而是把项目往“可交付、可协作、可放到 GitHub”方向推进了一层：

- 清理默认模板文件和运行产物
- 完善 `.gitignore` 与 `.dockerignore`
- 增加 `README.md`
- 增加架构总览和文档索引
- 增加 `Dockerfile + docker-compose.yml`
- 增加基础 GitHub Actions CI
- 增加 `/health` 健康检查接口

## 2. 为什么这一步重要

到这个阶段，项目的核心能力已经比较完整。再继续只加功能，收益会越来越小；但如果没有交付层，面试和 GitHub 展示时会出现两个问题：

1. 项目“能讲”，但不够像正式工程项目
2. 代码一旦继续迭代，就缺少最基础的自动验证

所以这一步的重点不是新增业务能力，而是提高工程完成度。

## 3. 新增的交付层内容

### Docker 化

新增文件：

- [docker-compose.yml](D:/Code/Fastapi/AgentNews/docker-compose.yml)
- [backend/Dockerfile](D:/Code/Fastapi/AgentNews/backend/Dockerfile)
- [frontend/Dockerfile](D:/Code/Fastapi/AgentNews/frontend/Dockerfile)
- [frontend/nginx.conf](D:/Code/Fastapi/AgentNews/frontend/nginx.conf)

当前方案的定位是：

- MySQL 和 Redis 独立容器
- Backend 独立容器
- Frontend 静态构建后由 Nginx 托管
- Qdrant 当前仍走 backend 内部 local persistent mode

这样做的原因：

- 现在最重要的是把检索架构跑通，而不是先把 Qdrant 服务化部署做复杂
- 本地 Qdrant 模式更利于单机开发和演示
- 后面如果切到独立 Qdrant 服务，改的是部署形态，不是整体检索架构

### 健康检查

新增接口：

- `GET /health`

意义：

- 让部署后能快速判断服务是否启动成功
- 为后续容器编排、CI smoke check 和可观测性预留入口

### GitHub Actions CI

新增文件：

- [.github/workflows/ci.yml](D:/Code/Fastapi/AgentNews/.github/workflows/ci.yml)

当前 CI 做的是最基础但最有价值的几件事：

- 后端依赖安装 + targeted compile + app import
- backend smoke
- backend integration
- frontend build

这还不是完整测试体系，但已经能挡住最常见的回归：

- 后端语法错误
- FastAPI 应用导入错误
- 前端打包失败
- 会话主链路回归

## 4. 仓库清理

这一层还清理了：

- 默认 Vite 模板残留文件
- `.cursor / .idea / __pycache__ / debug log / 本地 qdrant 索引 / eval jsonl`

这些内容本地开发可能会重新生成，但现在已经通过 ignore 规则收口，不会继续污染仓库。

## 5. 和整体计划的关系

这一层属于最初路线图里的 `M4 工程化收尾`。  
它不是“主功能实现”的一部分，而是把项目从“研究型作品”往“企业化交付作品”推进的关键步骤。

## 6. 面试里怎么讲

可以这样概括：

核心功能完成后，我没有停在“能跑”，而是继续补了交付层，包括 Docker Compose、健康检查、README、架构总览和 GitHub Actions CI。这样项目在 GitHub 上不仅能展示功能，也能体现基本的工程交付能力。
