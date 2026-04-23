# M1.3 + M1.4：浏览量聚合回刷与热榜基础能力

## 目标

这一阶段把新闻详情页的浏览量更新从“每次请求直接写 MySQL”升级成：

- 详情访问先写 Redis 增量
- 后端后台任务定时批量回刷 MySQL
- 基于 Redis `ZSET` 维护热门新闻排行
- Redis 异常时自动降级到 MySQL，保证功能不中断

这一步是新闻项目从“能跑”走向“企业级可扩展”的关键。

## 设计概览

### 1. 浏览量增量键

```text
news:views:delta:{news_id}
```

用途：

- 记录某条新闻自上次回刷以来新增的浏览量
- 详情页访问时只做 `INCR`
- 减少高频写对 MySQL 的直接压力

### 2. 热榜键

```text
news:hot:global
news:hot:{category_id}
```

用途：

- 使用 Redis `ZSET` 维护全站热榜和分类热榜
- 每次详情访问同时对全局热榜和分类热榜加分
- 热榜接口优先从 Redis 获取排名，缺失时回退到 MySQL 视图排序

### 3. 回刷机制

后台任务周期性执行：

1. 扫描 `news:views:delta:*`
2. 原子取出每个增量值
3. 批量写回 MySQL
4. 成功后同步更新详情缓存中的基础 `views`
5. 写回失败时把增量恢复到 Redis

## 为什么这样设计

### 1. 避免高频直写数据库

新闻详情页是典型高读高写入口。每次详情访问都更新 MySQL 会带来：

- 数据库写压力增加
- 事务频繁提交
- 排行计算成本上升

改成 Redis 聚合后，MySQL 只承接低频批量更新。

### 2. 保持用户感知实时

虽然 MySQL 是延迟回刷，但详情接口会把：

- 缓存里的基础 `views`
- Redis 当前增量 `delta`

进行叠加返回，所以用户看到的浏览量仍然是实时增长的。

### 3. Redis 不再是单点硬依赖

如果 Redis 暂时不可用：

- 详情接口自动回退到旧的 MySQL 自增逻辑
- 热榜接口自动回退到 MySQL 按 `views desc, publish_time desc` 排序

这样不会因为缓存层异常导致主业务不可用。

## 代码结构

新增/调整的核心模块：

- `backend/cache/keys.py`
  - 新增浏览量增量键和热榜键
- `backend/cache/news_cache.py`
  - 新增浏览量记录、增量读取、增量回收、热榜 ID 获取
- `backend/crud/news.py`
  - 新增批量写回浏览量、按 ID 批量获取新闻、热榜回退查询
- `backend/services/news_service.py`
  - 详情页改为 Redis 增量计数
  - 新增热门新闻服务
- `backend/tasks/news_metrics.py`
  - 新增浏览量回刷任务
- `backend/main.py`
  - 启动时注册后台回刷循环

## 环境变量

新增：

```env
VIEW_FLUSH_INTERVAL_SECONDS=60
```

含义：

- 控制后台把 Redis 浏览量增量刷回 MySQL 的周期
- 默认 `60` 秒

开发期建议保留 `60` 秒，便于手工测试。

## 接口变化

新增接口：

```http
GET /api/news/hot?categoryId=1&limit=10
```

参数：

- `categoryId`：可选，不传表示全站热榜
- `limit`：返回条数，范围 `1-20`

返回结构：

- 与新闻列表项一致
- `views` 会叠加 Redis 尚未回刷的实时增量

## 手工测试建议

### 1. 验证详情浏览量实时增长

1. 启动后端和前端
2. 打开任意新闻详情页
3. 连续刷新 3-5 次
4. 观察详情页返回的 `views` 是否持续增长

预期：

- 即使 MySQL 尚未更新，接口返回的浏览量也会立即增加

### 2. 验证热榜接口

1. 先多次访问同一条新闻详情
2. 请求：

```http
GET /api/news/hot
```

或：

```http
GET /api/news/hot?categoryId=1&limit=5
```

预期：

- 刚刚频繁访问的新闻应更靠前
- 即使还未回刷 MySQL，热榜也应先反映到 Redis 排序里

### 3. 验证回刷生效

1. 记住某条新闻当前 `views`
2. 连续访问该详情页几次
3. 等待 `VIEW_FLUSH_INTERVAL_SECONDS` 到达
4. 再查看数据库或重启接口后重新查询详情

预期：

- MySQL 中的 `views` 会被批量补齐
- 详情接口回刷后仍然维持正确的累计浏览量，不会回退

### 4. 验证 Redis 降级

1. 在本地暂停 Redis
2. 继续请求新闻详情和热榜接口

预期：

- 新闻详情仍能访问
- 浏览量会回退为直接写 MySQL
- 热榜接口会回退为数据库排序结果

## 面试可讲的点

- 为什么浏览量适合 Redis 聚合而不是强一致直写 MySQL
- 为什么热榜适合 `ZSET`
- 如何保证 Redis 异常时业务可降级
- 如何保证回刷后详情缓存的 `views` 不回退
- 为什么把“列表/详情缓存”和“浏览量计数”拆成两套缓存职责
