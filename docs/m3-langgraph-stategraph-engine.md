# M3.16 LangGraph StateGraph Engine

## 鏈鍋氫簡浠€涔?
杩欎竴闃舵鎶婃柊闂?Agent 浠庘€淟angGraph 鎬濇兂灞傗€濇帹杩涘埌浜嗏€淟angGraph 瀹樻柟 `StateGraph` 璇硶灞傗€濄€?
鍦ㄤ笂涓€闃舵锛岄」鐩凡缁忓叿澶囦簡杩欎簺缁撴瀯锛?
- 缁熶竴 `WorkflowState`
- 鏄庣‘鑺傜偣杈圭晫
- `workflowTrace`
- LangSmith SDK tracing

浣嗗綋鏃跺伐浣滄祦鏈綋浠嶇劧鏄嚜瀹氫箟 Python 鐘舵€佹祦锛屽彧鏄璁′笂鍙傝€冧簡 LangGraph銆?
杩欎竴娆℃柊澧炰簡鐪熸鐨?`StateGraph` 鎵ц寮曟搸锛屽苟閫氳繃 `AGENT_WORKFLOW_ENGINE` 鍒囨崲涓诲叆鍙ｏ細

- `legacy`锛氫繚鐣欏師鏉ョ殑鑷畾涔夌姸鎬佹祦
- `langgraph`锛氬惎鐢ㄥ畼鏂?`StateGraph` 宸ヤ綔娴?
褰撳墠榛樿璧?`langgraph`銆?
## 涓轰粈涔堣杩欎箞鍋?
### 1. 涔嬪墠鍙湁 LangGraph 鐨勬€濇兂锛屼笉鏄畼鏂硅娉?
涔嬪墠鐨勫疄鐜版湰璐ㄤ笂鏄細

```text
state -> node -> trace
```

杩欏凡缁忓緢鎺ヨ繎 LangGraph锛屼絾杩樹笉鏄畼鏂?API銆?
闈㈣瘯閲屽鏋滃彧璇粹€滄垜鐢ㄤ簡 LangGraph鈥濓紝浼氭湁涓€涓闄╋細

- 闈㈣瘯瀹樼户缁拷闂?`StateGraph`銆乣add_node`銆乣add_edge`銆乣compile`
- 浣犱細鍙戠幇鑷繁瀹為檯椤圭洰閲屽苟娌℃湁鐪熸浣跨敤杩欎簺璇硶

鎵€浠ヨ繖涓€闃舵蹇呴』琛ラ綈銆?
### 2. LangSmith 鍥捐鍥炬洿渚濊禆鐪熸鐨?Graph 鎵ц

浣犱箣鍓嶅湪 LangSmith 閲岀湅鍒扮殑鏇村鏄?trace / run / span銆?
鍘熷洜涓嶆槸 LangSmith 涓嶈锛岃€屾槸褰撴椂宸ヤ綔娴佹墽琛屾柟寮忚繕鏄嚜瀹氫箟 Python 娴佺▼銆? 
LangSmith 鑳界湅鍒?tracing锛屼絾瀹冩嬁鍒扮殑涓嶆槸涓€涓湡姝ｇ敱 `StateGraph` 椹卞姩鐨?graph run銆?
杩欎竴娆℃敼鎴?`StateGraph` 鍚庯紝閾捐矾浼氭洿鎺ヨ繎瀹樻柟鏂囨。閲屽睍绀虹殑鍥惧舰鍖栬妭鐐圭粨鏋勫拰鑺傜偣鎵ц瑙嗗浘銆?
### 3. 杩欎竴姝ヨ兘鎶娾€滄€濇兂灞傗€濆彉鎴愨€滆娉曞眰鈥?
涔嬪墠浣犲彲浠ヨ锛?
> 鎴戞寜 LangGraph 鐨勭姸鎬佹祦鎬濇兂璁捐浜嗗伐浣滄祦銆?
鐜板湪浣犲彲浠ヨ繘涓€姝ヨ锛?
> 鎴戝厛鎸?LangGraph 鎬濇兂鎶?Agent 鎷嗘垚 stateful workflow锛屽悗缁啀杩佺Щ鍒板畼鏂?`StateGraph` 璇硶锛岃繖鏍疯妭鐐广€佺姸鎬併€乼race 鐨勮竟鐣岄兘鏇存竻妤氾紝涔熸洿鍒╀簬 LangSmith 瑙傛祴銆?
杩欎釜璇存硶浼氭洿瀹屾暣锛屼篃鏇寸粡寰椾綇娣遍棶銆?
## 杩欎竴闃舵鐨勫疄鐜板師鐞?
### 1. StateGraph 鏄粈涔?
`StateGraph` 鏄?LangGraph 瀹樻柟鐨勫浘缂栨帓鍏ュ彛銆? 
浣犲彲浠ユ妸瀹冪悊瑙ｄ负锛?
- `state`锛氭暣鏉″伐浣滄祦鍏变韩鐨勬暟鎹璞?- `node`锛氭瘡涓鐞嗘楠?- `edge`锛氳妭鐐逛箣闂存€庝箞娴佽浆
- `compile()`锛氭妸澹版槑寮忓浘缁撴瀯缂栬瘧鎴愬彲鎵ц宸ヤ綔娴?
褰撳墠椤圭洰閲岀殑鑺傜偣鏄細

- `query-analysis`
- `retrieval-planner`
- `retrieval`
- `route-filter`
- `final-rerank`
- `generator`
- `verifier`
- `response-formatter`
- `no-evidence-response`

### 2. 涓轰粈涔堟湁 `no-evidence-response`

杩欐槸涓€涓樉寮忓垎鏀妭鐐广€?
濡傛灉 `final-rerank` 涔嬪悗娌℃湁瓒冲璇佹嵁锛屽氨涓嶈繘鍏ョ敓鎴愯妭鐐癸紝鑰屾槸鐩存帴杩涘叆鎷掔瓟鑺傜偣銆?
杩欑被鑺傜偣璁捐寰堥€傚悎鏂伴椈 Agent锛屽洜涓烘柊闂婚棶绛旈潪甯稿己璋冿細

- 鏈夎瘉鎹啀鍥炵瓟
- 娌¤瘉鎹氨鎷掔瓟
- 涓嶉潬妯″瀷纭紪

### 3. 杩欐涓嶆槸鎺ㄧ炕鏃ч€昏緫锛岃€屾槸鎹㈡墽琛屽唴鏍?
鏃х増鏈殑涓氬姟鑳藉姏娌℃湁琚帹缈伙細

- Query Analysis
- Retrieval Planner
- Local/Web Retrieval
- Route-Aware Filtering
- Final Rerank
- Verifier
- Formatter

閮借繕鍦ㄣ€?
鍙樺寲鍦ㄤ簬锛?
- 浠ュ墠鏄墜鍔ㄤ覆杩欎簺鏈嶅姟
- 鐜板湪鏄妸杩欎簺鏈嶅姟鏄犲皠鎴?`StateGraph` 鑺傜偣

杩欎篃鏄负浠€涔堟垜涓€鐩村潥鎸佸厛鍋氣€滅姸鎬佸寲宸ヤ綔娴佲€濓紝鍐嶈縼绉诲埌瀹樻柟 LangGraph 璇硶銆?
## 褰撳墠浣犺鎬庝箞鐞嗚В LangGraph 鍜?LangSmith 鐨勫叧绯?
### 1. LangGraph 璐熻矗鎵ц缁撴瀯

LangGraph 瑙ｅ喅鐨勬槸锛?
- 鐘舵€佹€庝箞娴佽浆
- 鑺傜偣鎬庝箞鎷?- 鍒嗘敮鎬庝箞璺?- 鍝簺鑺傜偣鏄『搴忥紝鍝簺鏄潯浠惰烦杞?
### 2. LangSmith 璐熻矗瑙傛祴

LangSmith 瑙ｅ喅鐨勬槸锛?
- 姣忚疆 run 鐨?trace
- 姣忎釜鑺傜偣鎵ц浜嗕粈涔?- 鍝釜鑺傜偣鎱?- 鍝釜鑺傜偣澶辫触
- prompt / retriever / verifier 鐨勮涓烘槸鍚︾鍚堥鏈?
鎵€浠ユ渶鍑嗙‘鐨勫叧绯绘槸锛?
```text
LangGraph = workflow runtime
LangSmith = observability / tracing / evaluation
```

## 鏈鏀瑰姩鍚庣殑鐘舵€?
褰撳墠椤圭洰閲屽叧浜?Agent 宸ヤ綔娴佺殑璇存硶搴旇鏇存柊涓猴細

- 宸ヤ綔娴佹墽琛岋細`LangGraph StateGraph`
- 鍙娴嬫€э細`LangSmith SDK tracing + 鏈湴 run log`
- 椤圭洰褰㈡€侊細`LangGraph-ready` 宸插崌绾т负 `LangGraph syntax active`

## 濡備綍娴嬭瘯

### 1. 鐘舵€佹帴鍙?
璁块棶锛?
- `GET /api/ai/status`

閲嶇偣纭锛?
- `workflowEnabled = true`
- `workflowEngine = "langgraph"`
- `workflowStyle = "langgraph-stategraph"`
- `graphVisualizationReady = true`

### 2. 鍓嶇鐘舵€?
鎵撳紑 AI 椤碉紝椤堕儴搴旂湅鍒帮細

- `Workflow LangGraph`
- `Graph Ready`
- `LangSmith Configured` 鎴?`Ready`

### 3. 鐪熷疄闂瓟

鍙戣捣涓€杞?AI 闂瓟鍚庯細

- 鍓嶇浠嶅簲鏄剧ず `workflowSummary`
- 姣忎釜鑺傜偣 trace 浠嶅簲瀛樺湪
- LangSmith 骞冲彴閲屽簲鏇村鏄撶湅鍒?graph 瑙嗗浘鍜岃妭鐐规墽琛?
### 4. 鍒囨崲鍥炴棫寮曟搸

濡傛灉浣犳兂楠岃瘉寮曟搸鍒囨崲鏈哄埗锛屽彲浠ュ湪 `.env` 閲屾敼锛?
```env
AGENT_WORKFLOW_ENGINE=legacy
```

閲嶅惎鍚庣鍚庡啀璁块棶鐘舵€佹帴鍙ｏ紝搴旂湅鍒版棫宸ヤ綔娴佹ā寮忋€?
## 闈㈣瘯鎬庝箞璁?
鎺ㄨ崘璇存硶锛?
> 鎴戜竴寮€濮嬫病鏈夌洿鎺ヤ负浜嗙敤妗嗘灦鑰岀敤 LangGraph锛岃€屾槸鍏堟妸鏂伴椈 Agent 涓婚摼璺噸鏋勬垚 stateful workflow锛屾媶娓呮 query analysis銆乸lanner銆乺etrieval銆乫ilter銆乺erank銆乬enerator銆乿erifier銆乫ormatter 杩欎簺鑺傜偣銆傜瓑鐘舵€佽竟鐣屽拰 trace 閮界ǔ瀹氫箣鍚庯紝鍐嶈縼绉诲埌 LangGraph 瀹樻柟 `StateGraph` 璇硶銆傝繖鏍?LangSmith 涓嶄粎鑳界湅 trace锛屼篃鏇村鏄撳睍绀哄浘缁撴瀯鍜岃妭鐐规墽琛屾儏鍐点€?
## 瀹樻柟璧勬枡

- [LangGraph 瀹樻柟鏂囨。](https://docs.langchain.com/langgraph)
- [LangSmith: Trace with LangGraph](https://docs.langchain.com/langsmith/trace-with-langgraph)

