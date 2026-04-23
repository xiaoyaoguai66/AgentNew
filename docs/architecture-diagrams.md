# AgentNews 架构图集

这份文档只做一件事：把项目里最值得展示的几张图单独收口，方便你后续截图、贴到 GitHub，或者面试时直接打开讲。

## 1. 系统总览图

```mermaid
flowchart LR
    UI["Vue Mobile App"] --> API["FastAPI API Layer"]
    API --> SVC["Service Layer"]
    SVC --> MYSQL["MySQL"]
    SVC --> REDIS["Redis Cache / Hot Rank / Session State"]
    SVC --> QDRANT["Qdrant Local Vector Index"]
    SVC --> TAVILY["Tavily Web Search"]
    SVC --> LLM["LLM / Embedding Provider"]
    SVC --> LANGGRAPH["LangGraph StateGraph"]
    LANGGRAPH --> LANGSMITH["LangSmith Tracing"]
```

适合：

- README
- GitHub 首页
- 面试开场

## 2. 新闻 Agent 工作流图

```mermaid
flowchart LR
    Q["Question"] --> QA["Query Analysis"]
    QA --> RP["Retrieval Planner"]
    RP --> LR["Local Retrieval"]
    RP --> WR["Web Search"]
    LR --> RF["Route-Aware Filter"]
    WR --> RF
    RF --> RR["Final Rerank"]
    RR --> GEN["Generator"]
    GEN --> VER["Verifier"]
    VER --> FMT["Response Formatter"]
    FMT --> OUT["Answer / Sources / Trace / Follow-ups"]
```

适合：

- 讲 Agent 结构
- 解释为什么不是自由 Agent

## 3. 会话与记忆图

```mermaid
flowchart LR
    UI["AIChat Session Drawer"] --> SID["sessionId"]
    SID --> INDEX["Redis Session Index"]
    SID --> STATE["Redis Session State"]
    STATE --> RECENT["Recent Messages"]
    STATE --> SUMMARY["Summary Memory"]
    RECENT --> PROMPT["Prompt Context"]
    SUMMARY --> PROMPT
    PROMPT --> AGENT["LangGraph Workflow"]
```

适合：

- 讲 session memory
- 讲聊天窗口管理
- 解释“记忆”和“会话列表”的区别

## 4. 评测闭环图

```mermaid
flowchart LR
    DATASET["Eval Dataset"] --> RUN["Eval Run"]
    RUN --> RESULT["Eval Result"]
    RESULT --> FAIL["Failure Cases"]
    FAIL --> TUNE["Heuristic / Guardrail Tuning"]
    TUNE --> RUN
    RUN --> LANGSMITH["LangSmith Eval / Trace"]
```

适合：

- 讲为什么项目不是只会回答
- 讲调优闭环和失败样本沉淀

## 5. 使用建议

如果你后面只想挑 1 到 2 张图放到 GitHub 首页，优先用：

1. 系统总览图
2. 新闻 Agent 工作流图

如果是面试里细讲，再补：

3. 会话与记忆图
4. 评测闭环图
