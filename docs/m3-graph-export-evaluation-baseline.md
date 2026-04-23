# M3.17 Workflow Graph Export And Evaluation Baseline

## 鏈鍋氫簡浠€涔?
杩欎竴闃舵琛ヤ簡涓ょ被鑳藉姏锛?
1. `Workflow Graph Export`
2. `Evaluation Baseline`

鍓嶈€呰В鍐斥€滃伐浣滄祦鍥惧埌搴曟€庝箞灞曠ず鈥濓紝鍚庤€呰В鍐斥€滆繖濂?query analysis / planner 鎬庝箞楠岃瘉涓嶆槸鎷嶈剳琚嬧€濄€?
鏂板鎺ュ彛锛?
- `GET /api/ai/workflow/graph`
- `GET /api/ai/eval/dataset`
- `POST /api/ai/eval/run`

## 涓轰粈涔堣鍋?Workflow Graph Export

浣犲墠闈㈡彁鍒颁竴涓緢鍏抽敭鐨勯棶棰橈細

> 涔嬪墠濂藉儚鑳藉湪 studio 閲岀湅鍒板浘

杩欎釜璁板繂鏈韩娌℃湁闂銆? 
鍙槸瑕佸垎娓呮锛?
- `LangSmith` 鏇村亸 tracing / evaluation / run 瑙傚療
- `LangGraph Studio` 鎴?graph 瑙嗗浘鏇村亸 workflow 缁撴瀯灞曠ず

涓轰簡璁╅」鐩嚜宸变篃鑳界洿鎺ュ鍑哄浘缁撴瀯锛岃繖涓€闃舵鎴戣ˉ浜?`workflow graph export`銆?
鐜板湪鍚庣浼氳繑鍥烇細

- `nodes`
- `edges`
- `mermaid`

杩欐牱灏辩畻涓嶄緷璧?Studio锛屼篃鍙互锛?
- 鍦ㄦ帴鍙ｉ噷鐩存帴鐪嬪浘缁撴瀯
- 鎶?Mermaid 鏀捐繘 GitHub README
- 鍦ㄩ潰璇曟椂鏄庣‘灞曠ず鑺傜偣鍜岃竟

## 涓轰粈涔堣鍏堝仛 Evaluation Baseline

褰撳墠鏂伴椈 Agent 宸茬粡鏈夊緢澶氱幆鑺傦細

- Query Analysis
- Retrieval Planner
- Local / Web Retrieval
- Route Filter
- Final Rerank
- Verifier
- Formatter

浣嗗鏋滄病鏈夎瘎娴嬶紝浣犲緢闅剧郴缁熷洖绛旇繖浜涢棶棰橈細

- Planner 鍒嗗緱鍑嗕笉鍑?- Query Analysis 鐨?intent 鍒ゆ柇绋充笉绋?- freshness / scope 杩欎簺瀛楁鏄笉鏄悎鐞?
鎵€浠ヨ繖涓€闃舵鍏堝仛浜嗕竴涓?*缁撴瀯鍖栨湰鍦拌瘎娴嬪熀绾?*锛屼紭鍏堣瘎娴嬶細

- `expectedPlan`
- `expectedIntent`
- `expectedFreshness`
- `expectedScope`

杩欐槸涓€绉嶉潪甯搁€傚悎涓湡椤圭洰鐨勫仛娉曪紝鍥犱负瀹冿細

- 涓嶄緷璧栧ぇ妯″瀷杈撳嚭绋冲畾鎬?- 涓嶄緷璧栬仈缃戠粨鏋滄尝鍔?- 鍙互鍏堥獙璇佹绱㈠墠閾捐矾鏄惁鍚堢悊

涔熷氨鏄厛鎶娾€滃墠鍗婃宸ヤ綔娴佲€濊瘎绋筹紝鍐嶇户缁仛鈥滃畬鏁撮棶绛旀晥鏋滆瘎娴嬧€濄€?
## 鎶€鏈惈涔?
### 1. Workflow Graph Export

瀹冪殑浣滅敤鏄妸宸ヤ綔娴佷粠鈥滀唬鐮侀噷鐨勫浘鈥濆彉鎴愨€滃彲瑙傚療鐨勫浘鈥濄€?
褰撳墠浼氬鍑轰笁绉嶄俊鎭細

- `nodes`锛氳妭鐐瑰垪琛?- `edges`锛氳妭鐐逛箣闂寸殑杈?- `mermaid`锛氬彲鐩存帴澶嶅埗鍒?Markdown 鐨勬祦绋嬪浘鏂囨湰

### 2. Evaluation Dataset

杩欎笉鏄缁冮泦锛岃€屾槸**璇勬祴闆?*銆? 
涔熷氨鏄竴缁勫甫棰勬湡鏍囩鐨勯棶棰樻牱鏈紝鐢ㄦ潵妫€楠岀郴缁熻涓恒€?
褰撳墠璇勬祴闆嗗瓧娈靛寘鎷細

- `question`
- `mode`
- `timeRange`
- `category`
- `expectedPlan`
- `expectedIntent`
- `expectedFreshness`
- `expectedScope`

### 3. Evaluation Baseline

杩欓噷鐨?baseline 涓嶆槸鈥滄渶缁堟ā鍨嬭兘鍔涒€濓紝鑰屾槸鈥滃綋鍓嶉樁娈垫渶鍏堣绋冲畾鐨勮瘎娴嬪熀绾库€濄€?
鍥犱负濡傛灉 Query Analysis 鍜?Planner 鏈韩灏变笉绋冲畾锛屽悗闈㈠啀鎺ワ細

- rerank
- verifier
- full answer evaluation

涔熶細瓒婃潵瓒婇毦瑙ｉ噴銆?
## 鏈瀹炵幇鍘熺悊

### 1. Graph Export

濡傛灉褰撳墠寮曟搸鏄?`langgraph`锛?
- 鐩存帴璇诲彇 `CompiledStateGraph`
- 鎷垮埌 graph 鍐呴儴鐨?`nodes / edges`
- 鍐嶅鍑烘垚 Mermaid

濡傛灉褰撳墠寮曟搸鏄?`legacy`锛?
- 鐢ㄩ潤鎬佽妭鐐瑰畾涔夎ˉ涓€浠藉吋瀹瑰浘

鎵€浠ヨ繖濂楁帴鍙ｆ棦鑳芥敮鎸佺幇鍦ㄧ殑 `LangGraph`锛屼篃鑳藉吋瀹瑰洖閫€妯″紡銆?
### 2. Evaluation Baseline

璇勬祴娴佺▼鏄細

```text
load eval dataset
-> run query analysis
-> run retrieval planner
-> compare with expected labels
-> compute planner / intent / freshness / scope accuracy
```

杩欎竴姝ヨ繕娌℃湁鍘昏瘎娴嬶細

- 鏈€缁堝洖绛旀枃鏈槸鍚﹀畬缇?- Web 缁撴灉鏄惁鎬绘槸鏈€浼?- LLM 鐨勭敓鎴愯川閲?
杩欐槸鏈夋剰鎺у埗鑼冨洿锛屽洜涓鸿繖涓€闃舵鍏堣鎶?*缁撴瀯鍖栧伐浣滄祦鍓嶅崐娈?*璇勭ǔ銆?
## 濡備綍娴嬭瘯

### 1. 宸ヤ綔娴佸浘

璁块棶锛?
- `GET /api/ai/workflow/graph`

閲嶇偣鐪嬶細

- `engine`
- `style`
- `graphVisualizationReady`
- `nodes`
- `edges`
- `mermaid`

濡傛灉褰撳墠鏄?LangGraph 妯″紡锛岄鏈燂細

- `engine = "langgraph"`
- `style = "langgraph-stategraph"`
- `graphVisualizationReady = true`

### 2. 璇勬祴闆?
璁块棶锛?
- `GET /api/ai/eval/dataset`

搴旇兘鐪嬪埌鍐呯疆娴嬭瘯鏍锋湰銆?
### 3. 璺戣瘎娴?
璇锋眰锛?
- `POST /api/ai/eval/run`

绀轰緥 body锛?
```json
{
  "limit": 6
}
```

杩斿洖閲岄噸鐐圭湅锛?
- `plannerAccuracy`
- `intentAccuracy`
- `freshnessAccuracy`
- `scopeAccuracy`
- `results`

## 闈㈣瘯鎬庝箞璁?
鎺ㄨ崘琛ㄨ堪锛?
> 鍦ㄥ伐浣滄祦鎼捣鏉ヤ箣鍚庯紝鎴戞病鏈夌洿鎺ュ仠鍦ㄢ€滆兘璺戔€濓紝鑰屾槸缁х画鍋氫簡涓や欢浜嬨€傜涓€鏄妸 LangGraph 宸ヤ綔娴佸鍑烘垚缁撴瀯鍖?graph 鍜?Mermaid锛屾柟渚垮湪椤圭洰鏂囨。鍜?GitHub 閲屽睍绀鸿妭鐐逛笌杈癸紱绗簩鏄厛鏋勫缓浜嗕竴涓粨鏋勫寲璇勬祴鍩虹嚎锛屼紭鍏堥獙璇?Query Analysis 鍜?Retrieval Planner 鐨勮涓烘槸鍚︾鍚堥鏈熴€傝繖鏍峰悗闈㈠啀鍋氬畬鏁撮棶绛旇瘎娴嬪拰 LangSmith evaluation 鏃讹紝閾捐矾浼氭洿瀹规槗瑙ｉ噴銆?
