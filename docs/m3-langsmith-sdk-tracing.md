# M3.15 姝ｅ紡鎺ュ叆 LangSmith SDK Tracing

## 杩欎竴姝ュ仛浜嗕粈涔?
杩欎竴闃舵鎶婇」鐩粠 `LangSmith-ready` 鎺ㄨ繘鍒颁簡 **鍙€夊紑鍚殑 LangSmith 瀹樻柟 SDK tracing**銆?
鏈鏀瑰姩鍖呮嫭锛?
1. 瀹夎 `langsmith` Python SDK
2. 鍦?`observability` 灞傞泦涓鐞?LangSmith 閰嶇疆鍜屽鎴风
3. 鎶婄幇鏈?stateful workflow 鐨勫叧閿妭鐐规帴鍏ュ畼鏂?tracing
4. 淇濈暀鍘熸湁鏈湴 `workflowTrace` 鍜?`run log`
5. 鍓嶇缁х画鏄剧ず锛?   - `Trace / Run`
   - `Observability`
   - `LangSmith`

涔熷氨鏄锛岀幇鍦ㄧ郴缁熸湁涓ゅ眰瑙傛祴锛?
- 椤圭洰鑷繁鐨勬湰鍦板伐浣滄祦杞ㄨ抗
- LangSmith 瀹樻柟骞冲彴 trace

## 涓轰粈涔堣繖鏍峰仛

鍒颁笂涓€闃舵涓烘锛岄」鐩凡缁忔湁锛?
- state
- node
- workflow trace
- traceId / runId
- local run log

鎵€浠ヨ繖鏃舵渶鍚堢悊鐨勪笅涓€姝ワ紝涓嶆槸绔嬪埢杩佺Щ `LangGraph` 璇硶锛岃€屾槸鍏堟妸 **瀹樻柟瑙傛祴骞冲彴** 鎺ヤ笂銆?
鍘熷洜寰堢洿鎺ワ細

1. 闈㈣瘯浠峰€兼洿楂? 
   浣犲彲浠ユ槑纭锛?   - 鏈湴 trace 鎬庝箞鍋?   - 瀹樻柟 trace 鎬庝箞鎺?   - 涓轰粈涔堝厛鏈湴銆佸悗骞冲彴

2. 瀵圭幇鏈変唬鐮佷镜鍏ユ洿灏? 
   鐜板湪宸茬粡鏈夋竻鏅拌妭鐐硅竟鐣岋紝缁欒繖浜涜妭鐐瑰姞 tracing 姣旀敼鍐欐垚鍥炬鏋舵洿绋炽€?
3. 鏇寸鍚堝伐绋嬫紨杩涢『搴? 
   鍏堣瑙傛祴璺戦€氾紝鍐嶇户缁仛 LangGraph 璇硶杩佺Щ锛岄闄╂洿浣庛€?
## 鍏抽敭鎶€鏈惈涔?
### `LangSmith SDK tracing`

杩欐槸瀹樻柟 Python SDK 鐨?tracing 鏂瑰紡銆? 
涓嶆槸浣犺嚜宸卞啓涓€涓棩蹇楁枃浠讹紝鑰屾槸鎶婅繍琛屾暟鎹€氳繃瀹樻柟 SDK 鍙戝埌 LangSmith 骞冲彴銆?
### `traceable`

瀹樻柟鎻愪緵鐨勮楗板櫒銆? 
瀹冨彲浠ョ粰鏅€氬嚱鏁般€佸紓姝ュ嚱鏁般€佹绱㈠嚱鏁般€佺敓鎴愬嚱鏁版墦 trace銆?
鍦ㄥ綋鍓嶉」鐩噷锛屾垜鎶婂畠鐢ㄥ湪浜嗭細

- `Query Analysis`
- `Retrieval Planner`
- `Local Retrieval`
- `Web Retrieval`
- `Route Filter`
- `Final Rerank`
- `Generator`
- `Verifier`
- `Response Formatter`
- 鏁翠釜 `AgentNews Workflow`

### `tracing_context`

瀹樻柟鎻愪緵鐨勪笂涓嬫枃銆? 
瀹冪殑浣滅敤鏄粰涓€鏁磋疆璋冪敤璁剧疆缁熶竴鐨勶細

- project
- metadata
- tags
- client

鎴戣繖閲岀敤瀹冩妸鏁磋疆闂瓟鎸傚湪涓€涓粺涓€鐨?workflow 涓婏紝鍐嶈鍚勪釜瀛愯妭鐐?trace 鑷姩褰掑埌杩欐潯閾捐矾涓嬮潰銆?
### `LangGraph-ready`

褰撳墠椤圭洰渚濈劧鏄細

- `LangGraph-ready`

涓嶆槸锛?
- 宸叉寮忎娇鐢?`StateGraph/add_node/add_edge`

杩欎竴姝ユ帴鐨勬槸 LangSmith锛屼笉鏄?LangGraph 璇硶鏈韩銆?
## 瀹炵幇鍘熺悊

### 1. observability 灞傜粺涓€绠＄悊 SDK

鏂板 / 閲嶆瀯锛?
- `backend/services/agent_observability_service.py`

瀹冭礋璐ｏ細

- 鍒ゆ柇 SDK 鏄惁瀹夎
- 鍒濆鍖?LangSmith client
- 鍚屾鐜鍙橀噺锛?  - `LANGSMITH_TRACING_V2`
  - `LANGSMITH_API_KEY`
  - `LANGSMITH_PROJECT`
  - `LANGSMITH_ENDPOINT`
- 鎻愪緵缁熶竴鐨勶細
  - `langsmith_traceable(...)`
  - `langsmith_context(...)`
  - `build_langsmith_extra(...)`

杩欐牱涓氬姟灞備笉鐩存帴鏁ｈ惤鐫€瀹樻柟 SDK 璋冪敤銆?
### 2. workflow 灞傝妭鐐瑰寲鎺?tracing

`backend/services/agent_workflow_service.py` 鐜板湪涓嶅彧鏄湰鍦拌褰?`workflowTrace`锛岃繕鎶婂叧閿妭鐐归€氳繃 `@traceable` 鎺ュ埌浜?LangSmith銆?
鎵€浠ョ幇鍦ㄤ竴杞棶绛斿悓鏃朵細浜х敓涓ょ杞ㄨ抗锛?
- 鏈湴杩斿洖缁欏墠绔殑 `workflowTrace`
- 瀹樻柟骞冲彴閲岀殑 LangSmith trace tree

### 3. 鏈湴 run log 浠嶇劧淇濈暀

鍗充娇 LangSmith 寮€鍚紝鏈湴浠嶄繚鐣欙細

- `backend/data/agent_runs/agent_runs.jsonl`

鍘熷洜鏄細

- 鏈湴璋冭瘯渚濈劧鏂逛究
- 骞冲彴涓嶅彲鐢ㄦ椂浠嶆湁闄嶇骇璁板綍
- 杩欐洿绗﹀悎浼佷笟椤圭洰鐨勨€滃灞傝娴嬧€濇€濊矾

## 褰撳墠閰嶇疆鏂瑰紡

`.env` 寤鸿鑷冲皯鏈夛細

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=浣犵殑_langsmith_key
LANGSMITH_PROJECT=agentnews-dev
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

### 褰撳墠閫昏緫

- 濡傛灉 `LANGSMITH_TRACING=false`
  - 鍙繚鐣欐湰鍦?run log
  - LangSmith 鐘舵€佹樉绀?`Ready` 鎴?`Off`

- 濡傛灉 `LANGSMITH_TRACING=true` 浣嗘病閰?key
  - 涓嶄細宕?  - 浠嶈蛋鏈湴 run log

- 濡傛灉 `LANGSMITH_TRACING=true` 涓旈厤浜?`LANGSMITH_API_KEY`
  - LangSmith tracing 姝ｅ紡鐢熸晥

## 濡備綍娴嬭瘯

### 1. 鏈湴鐘舵€?
璁块棶锛?
- `GET /api/ai/status`

閲嶇偣鐪嬶細

- `langsmithReady`
- `langsmithTracing`
- `langsmithConfigured`
- `observabilityEnabled`

### 2. 鏈湴 run log

鍙戜竴杞?AI 瀵硅瘽鍚庯細

- `GET /api/ai/runs/recent`
- 鏌ョ湅 `backend/data/agent_runs/agent_runs.jsonl`

閮藉簲璇ヨ兘鐪嬪埌鏂拌褰曘€?
### 3. LangSmith 骞冲彴

濡傛灉浣犲凡缁忓湪 `.env` 閰嶅ソ浜嗭細

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
```

閲嶅惎鍚庣锛屽啀鍙戣捣涓€杞?AI 瀵硅瘽銆?
棰勬湡锛?
1. `GET /api/ai/status` 杩斿洖锛?   - `langsmithConfigured = true`
2. LangSmith 瀹樻柟骞冲彴閲岃兘鐪嬪埌锛?   - `AgentNews Workflow`
   - 涓嬮潰鎸傜潃鍚勪釜瀛愯妭鐐?trace

## 杩欎竴姝ヤ箣鍚庝綘鎬庝箞璁?
鎺ㄨ崘璇存硶锛?
> 鎴戝綋鍓嶉」鐩凡缁忎笉鏄仠鐣欏湪 LangSmith-ready锛岃€屾槸琛ヤ簡瀹樻柟 SDK tracing銆傚叿浣撳仛娉曚笉鏄妸涓氬姟浠ｇ爜鍒板濉?tracing锛岃€屾槸鍏堟娊浜嗕竴灞?observability service锛屽湪閲岄潰缁熶竴绠＄悊 LangSmith client銆乼raceable decorator 鍜?tracing context銆傜劧鍚庢妸鐜版湁 stateful workflow 鐨勫叧閿妭鐐规帴鍒?LangSmith锛屽悓鏃朵繚鐣欐湰鍦?workflow trace 鍜?run log 浣滀负闄嶇骇瑙傛祴銆?
## 鍜?LangGraph 鐨勫叧绯?
杩欎竴姝ヤ粛鐒朵笉鏄?LangGraph 璇硶杩佺Щ锛岃€屾槸涓哄悗缁縼绉诲仛瑙傛祴鍩虹銆?
浣犵幇鍦ㄦ渶鍑嗙‘鐨勮〃杈炬槸锛?
1. 宸茬粡鎸?LangGraph 鎬濇兂鍋氫簡 stateful workflow
2. 宸茬粡鎸?LangSmith 鎬濇兂鍜?SDK 鍋氫簡杩愯瑙傛祴
3. 鍚庣画鍐嶅喅瀹氭槸鍚︽妸宸ヤ綔娴佹湰浣撹縼绉诲埌 LangGraph 瀹樻柟璇硶

