# M3.15 LangSmith SDK Tracing 娴嬭瘯娓呭崟

## 1. SDK 鏄惁瀹夎

纭鍚庣铏氭嫙鐜宸插畨瑁咃細

- `langsmith`

褰撳墠椤圭洰宸插啓鍏ワ細

- `backend/requirements.txt`

## 2. 鐜鍙橀噺

鏍圭洰褰?`.env` 寤鸿鑷冲皯閰嶇疆锛?
```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=浣犵殑_langsmith_key
LANGSMITH_PROJECT=agentnews-dev
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

濡傛灉鏆傛椂涓嶆兂鎺ュ畼鏂瑰钩鍙帮紝鍙互璁撅細

```env
LANGSMITH_TRACING=false
```

## 3. 鐘舵€佹帴鍙ｆ鏌?
璁块棶锛?
- `GET /api/ai/status`

閲嶇偣纭锛?
- `observabilityEnabled = true`
- `langsmithReady = true`
- `langsmithTracing = true/false`
- `langsmithConfigured = true/false`

### 棰勬湡

- 鍙 SDK銆佹病閰?key锛?  - `langsmithReady = true`
  - `langsmithConfigured = false`

- 閰嶅ソ tracing 鍜?key锛?  - `langsmithConfigured = true`

## 4. 鏈湴杩愯璁板綍妫€鏌?
鍙戣捣涓€杞?AI 瀵硅瘽鍚庯細

- `GET /api/ai/runs/recent`

棰勬湡杩斿洖鏈€杩戣繍琛岃褰曪紝骞跺寘鍚細

- `traceId`
- `runId`
- `startedAt`
- `finishedAt`
- `status`

鍚屾椂妫€鏌ワ細

- `backend/data/agent_runs/agent_runs.jsonl`

搴旇拷鍔犱竴鏉¤褰曘€?
## 5. 鍓嶇椤甸潰妫€鏌?
鎵撳紑 AI 椤碉紝椤堕儴搴旂湅鍒帮細

- `Observability Local`
- `LangSmith Ready` 鎴?`LangSmith Configured`

鍙戣捣涓€杞璇濆悗锛屽洖绛斿尯鍩熷簲鐪嬪埌锛?
- `Trace ...`
- `Run ...`

## 6. LangSmith 骞冲彴妫€鏌?
褰撳墠鎻愭槸 `.env` 宸查厤缃細

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
```

閲嶅惎鍚庣锛屽啀鍙戣捣涓€杞?AI 瀵硅瘽銆?
棰勬湡鍦?LangSmith 骞冲彴涓兘鐪嬪埌锛?
- `AgentNews Workflow`
- 瀛愯妭鐐癸細
  - `Query Analysis`
  - `Retrieval Planner`
  - `Local News Retrieval`
  - `Tavily Web Retrieval`
  - `Route Filter`
  - `Final Rerank`
  - `LLM Generation`
  - `Answer Verifier`
  - `Response Formatter`

## 7. 闄嶇骇妫€鏌?
鎶?`.env` 鏀规垚锛?
```env
LANGSMITH_TRACING=false
```

閲嶅惎鍚庣鍚庡啀娆℃祴璇曪細

棰勬湡锛?
- AI 鍔熻兘涓嶅彈褰卞搷
- 鏈湴 run log 浠嶇劧姝ｅ父
- 鍙槸 LangSmith 骞冲彴涓嶅啀鏂板 trace

