# M3.14 瑙傛祴灞備笌 LangSmith-Ready 璁捐

## 杩欎竴姝ュ仛浜嗕粈涔?
杩欎竴闃舵娌℃湁缁х画鏀规绱㈠拰鍥炵瓟绛栫暐锛岃€屾槸琛ヤ簡 Agent 鐨勮娴嬪眰锛?
1. 缁欐瘡杞?AI 瀵硅瘽鐢熸垚 `traceId` 鍜?`runId`
2. 鎶婅繍琛岀粨鏋滆惤鍒版湰鍦?`jsonl` run log
3. 鍦?`/api/ai/status` 閲屾毚闇?`Observability / LangSmith` 鐘舵€?4. 鏂板 `GET /api/ai/runs/recent` 璋冭瘯鎺ュ彛
5. 鍓嶇 AI 椤垫樉绀猴細
   - `Observability`
   - `LangSmith`
   - 姣忚疆鍥炵瓟鐨?`Trace / Run`

## 涓轰粈涔堣繖鏍峰仛

鍒?`M3.13` 涓烘锛岀郴缁熷凡缁忔湁锛?
- `state`
- `node`
- `trace`

杩欏凡缁忓緢鎺ヨ繎 `LangGraph / LangSmith` 鐨勫伐浣滄柟寮忎簡锛屼絾杩樺樊涓€灞傚伐绋嬮棴鐜細

- 姣忔杩愯鏈夋病鏈夊敮涓€ ID
- 姣忔杩愯鏈夋病鏈夋寔涔呭寲璁板綍
- 鍑洪敊鏃舵湁娌℃湁鐣欎笅澶辫触杞ㄨ抗
- 鍚庨潰濡傛灉鎺ュ畼鏂瑰钩鍙帮紝瑕佸線鍝噷瀵规帴

鎵€浠ヨ繖涓€姝ュ厛鍋氣€滄湰鍦扮増 LangSmith鈥濓細

- 鍏堟妸 `trace/run` 姒傚康璺戦€?- 鍏堟妸鏈湴璁板綍鑳藉姏鍋氬嚭鏉?- 鍚庨潰鍐嶆妸杩欎簺杩愯鏁版嵁鎺ュ埌瀹樻柟 LangSmith

杩欐牱鍋氱殑濂藉鏄紝鍚庨潰涓嶆槸鈥滀粠闆跺紑濮嬫帴骞冲彴鈥濓紝鑰屾槸鈥滄妸鐜版湁瑙傛祴鏁版嵁鍗囩骇鍒板畼鏂硅娴嬪钩鍙扳€濄€?
## 鍏抽敭鎶€鏈惈涔?
### `traceId`

涓€娆″畬鏁村伐浣滄祦閾捐矾鐨勬爣璇嗐€? 
浣犲彲浠ユ妸瀹冪悊瑙ｆ垚鈥滆繖涓€杞棶绛旂殑鎬昏拷韪彿鈥濄€?
### `runId`

涓€娆″叿浣撹繍琛屽疄渚嬬殑鏍囪瘑銆? 
鍦ㄥ綋鍓嶉」鐩噷锛屽畠鍜屼竴娆￠棶绛斿熀鏈竴涓€瀵瑰簲銆?
### `run log`

鏈湴杩愯鏃ュ織銆? 
褰撳墠淇濆瓨鍦細

- `backend/data/agent_runs/agent_runs.jsonl`

姣忎竴琛屽氨鏄竴鏉?JSON 杩愯璁板綍锛岄€傚悎鏈湴寮€鍙戝拰璋冭瘯銆?
### `LangSmith-ready`

鎰忔€濅笉鏄€滃凡缁忔帴浜嗗畼鏂?LangSmith SDK鈥濓紝鑰屾槸锛?
- 宸ヤ綔娴佸凡缁忔湁鑺傜偣
- 宸茬粡鏈夌粺涓€鐘舵€?- 宸茬粡鏈?trace
- 宸茬粡鏈?run log
- 宸茬粡鏈?LangSmith 鐩稿叧閰嶇疆浣?
涔熷氨鏄彧宸渶鍚庝竴姝ュ畼鏂?SDK / 骞冲彴鎺ョ嚎锛岃€屼笉鏄蹇靛拰缁撴瀯閮借繕娌″噯澶囧ソ銆?
## 浣犵幇鍦ㄥ埌搴曟槸鍦ㄧ敤 LangGraph 鐨勬€濇兂杩樻槸璇硶

褰撳墠椤圭洰鏄細

- **LangGraph 鐨勬€濇兂鍜屾灦鏋?*

涓嶆槸锛?
- **LangGraph 瀹樻柟 Python 璇硶**

鏇村噯纭湴璇达細

1. 浣犵幇鍦ㄥ凡缁忓湪鐢?`stateful workflow / node pipeline / trace` 杩欎竴濂?LangGraph 鎬濇兂
2. 浣嗕唬鐮侀噷杩樻病鏈夌湡姝ｅ紩鍏?`langgraph` 鍖咃紝涔熸病鏈夌敤瀹樻柟鐨?`StateGraph`銆乣add_node`銆乣add_edge`

鎵€浠ラ潰璇曟椂鏈€鍑嗙‘鐨勮娉曟槸锛?
> 褰撳墠椤圭洰宸茬粡鎸?LangGraph 鐨勭姸鎬佹祦鍜岃妭鐐圭紪鎺掓€濊矾閲嶆瀯鎴愪簡 stateful workflow锛屽苟璁板綍浜?workflow trace锛涗絾杩樻病鏈夋寮忚縼绉诲埌 LangGraph 瀹樻柟璇硶灞傦紝灞炰簬 LangGraph-ready 鑰屼笉鏄?LangGraph-SDK-native銆?
## LangSmith 鐜板湪鏄粈涔堢姸鎬?
褰撳墠椤圭洰鏄細

- **LangSmith-ready**

涓嶆槸锛?
- **宸茬粡姝ｅ紡鎺ュ叆 LangSmith 瀹樻柟 tracing**

浣犱箣鍓嶈寰椻€淟angSmith 瑕佸崟鐙啓涓€涓?py 鏂囦欢锛屾妸 API 閰嶅埌瀹樼綉鍘绘祴鈥濓紝杩欎釜鐞嗚В鏈変竴鍗婃槸瀵圭殑锛?
1. LangSmith 閫氬父纭疄闇€瑕佸崟鐙厤缃細
   - `LANGSMITH_TRACING`
   - `LANGSMITH_API_KEY`
   - `LANGSMITH_PROJECT`
2. 寰堝椤圭洰涔熺‘瀹炰細鍗曠嫭鍐欎竴涓?tracing/setup 妯″潡
3. 浣嗕笉鏄€滃繀椤诲崟鐙啓涓€涓?py 鏂囦欢鈥濊繖涓舰寮忔墠绠楁帴鍏?
鏈川涓婇渶瑕佺殑鏄細

- SDK tracing 鎵撳紑
- API Key 鍙敤
- 杩愯閾捐矾琚畼鏂?trace 鍒板钩鍙?
瀹樻柟鏂囨。鍙互鍙傝€冿細

- [LangGraph 瀹樻柟鏂囨。](https://docs.langchain.com/langgraph)
- [LangSmith: Trace with LangGraph](https://docs.langchain.com/langsmith/trace-with-langgraph)

## 褰撳墠瀹炵幇鍘熺悊

### 鍚庣

鏂板 `agent_observability_service.py`锛岃礋璐ｏ細

- 鍒涘缓 `traceId / runId`
- 璁板綍鎴愬姛杩愯
- 璁板綍澶辫触杩愯
- 璇诲彇鏈€杩戣繍琛岃褰?- 鏆撮湶 LangSmith-ready 鐘舵€?
`agent_workflow_service.py` 鐜板湪浼氾細

1. 杩涘叆宸ヤ綔娴佸墠鍏堝垱寤?`run_context`
2. 杩愯鎴愬姛鍚庤褰曞畬鏁?response
3. 杩愯澶辫触鍚庤褰曢儴鍒?trace 鍜?error
4. 鎶?`traceId / runId` 鐩存帴杩斿洖缁欏墠绔?
### 鍓嶇

AI 椤典細鏄剧ず锛?
- `Observability Local`
- `LangSmith Ready / Configured`
- 姣忔潯鍥炵瓟鐨?`Trace / Run`

杩欐剰鍛崇潃浣犲湪婕旂ず鏃跺彲浠ョ洿鎺ユ寚鐫€椤甸潰璁诧細

- 杩欐槸杩欒疆闂瓟鐨?trace id
- 杩欐槸杩欒疆杩愯鐨?run id
- 杩欐槸褰撳墠宸ヤ綔娴佽建杩?- 杩欐槸鏈湴 run log / 鍚庣画 LangSmith 鐨勬帴鍏ヤ綅

## 鐜鍙橀噺

鏂板杩欎簺閰嶇疆锛?
```env
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=agentnews-dev
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
AGENT_RUN_LOG_PATH=backend/data/agent_runs/agent_runs.jsonl
```

### 褰撳墠寤鸿

濡傛灉浣犺繕娌℃寮忔帴 LangSmith锛?
- `LANGSMITH_TRACING=false`
- 鍏堢敤鏈湴 run log

濡傛灉鍚庨潰瑕佹寮忔帴 LangSmith锛?
- `LANGSMITH_TRACING=true`
- 閰嶄笂 `LANGSMITH_API_KEY`
- 閰嶅ソ `LANGSMITH_PROJECT`

## 濡備綍娴嬭瘯

1. 閲嶅惎鍚庣
2. 璁块棶锛?   - `GET /api/ai/status`
3. 閲嶇偣纭锛?   - `observabilityEnabled = true`
   - `observabilityMode = local-trace-log`
   - `langsmithReady = true`
4. 鍙戣捣涓€杞?AI 瀵硅瘽
5. 鍦ㄨ繑鍥炰腑纭锛?   - `traceId`
   - `runId`
6. 璁块棶锛?   - `GET /api/ai/runs/recent`
7. 棰勬湡鑳界湅鍒版渶杩戣繍琛岃褰?8. 鎵撳紑鏈湴鏂囦欢锛?   - `backend/data/agent_runs/agent_runs.jsonl`
   涔熷簲璇ヨ兘鐪嬪埌瀵瑰簲璁板綍

## 闈㈣瘯鏃舵€庝箞璁?
鎺ㄨ崘璇存硶锛?
> 鎴戝綋鍓嶉」鐩凡缁忔寜 LangGraph 鐨勭姸鎬佹祦鍜岃妭鐐圭紪鎺掓€濊矾鎼垚浜?stateful workflow锛屽苟鎶?query analysis銆乸lanner銆乺etrieval銆乫ilter銆乺erank銆乬enerator銆乿erifier銆乫ormatter 閮芥媶鎴愪簡鏄惧紡鑺傜偣銆傚悓鏃讹紝鎴戞病鏈変竴寮€濮嬪氨纭帴 LangSmith锛岃€屾槸鍏堝仛浜嗘湰鍦?traceId銆乺unId 鍜?run log锛屾妸瑙傛祴閾捐矾璺戦€氥€傝繖鏍峰悗闈㈡帴 LangSmith 鏃讹紝涓嶆槸閲嶆柊璁捐宸ヤ綔娴侊紝鑰屾槸鎶婄幇鏈?trace/run 鏁版嵁鎺ュ埌瀹樻柟骞冲彴銆?
