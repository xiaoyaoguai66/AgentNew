# AgentNews 閫愭娴嬭瘯娓呭崟

## 浣跨敤鏂瑰紡

杩欎唤娓呭崟鐢ㄤ簬浣犳瘡娆℃敼瀹屽姛鑳藉悗锛屾寜椤哄簭楠岃瘉椤圭洰鏄惁杩樺鍦ㄥ彲杩愯鐘舵€併€?
寤鸿浣跨敤鏂瑰紡锛?
1. 鍏堝仛鐜涓庣姸鎬佹鏌?2. 鍐嶆祴鏂伴椈涓婚摼璺?3. 鍐嶆祴缂撳瓨涓庣儹姒?4. 鍐嶆祴 AI 鍔╂墜 / 妫€绱?/ 鍚戦噺绱㈠紩
5. 鏈€鍚庡仛涓€娆″墠鍚庣鏁翠綋鍥炲綊

---

## 涓€銆佺幆澧冧笌鍚姩妫€鏌?
### 1. 鍚庣鐜

纭锛?
- 鏍圭洰褰?`.env` 宸插瓨鍦?- `MYSQL_URL` 姝ｇ‘
- `REDIS_URL` 姝ｇ‘
- `LLM_API_KEY` 姝ｇ‘
- 濡傛灉鍚敤 Tavily锛宍TAVILY_API_KEY` 姝ｇ‘
- 濡傛灉鍚敤鍚戦噺妫€绱紝`LOCAL_RETRIEVAL_ENGINE=hybrid-ready`
- 濡傛灉鍚敤鍚戦噺妫€绱紝`ENABLE_VECTOR_RETRIEVAL=true`

鎺ㄨ崘鏄惧紡鍐欎笂锛?
```env
QDRANT_URL=
QDRANT_LOCAL_PATH=backend/data/qdrant
QDRANT_COLLECTION=agentnews_news_chunks
QDRANT_TIMEOUT_SECONDS=5

EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings
EMBEDDING_API_KEY=浣犵殑_key
EMBEDDING_MODEL=text-embedding-v4
```

璇存槑锛?
- `QDRANT_URL=` 涓虹┖鏄甯哥殑锛岃〃绀哄綋鍓嶄娇鐢ㄦ湰鍦?Qdrant 妯″紡
- `QDRANT_LOCAL_PATH` 鎸囧悜鏈湴绱㈠紩鐩綍

### 2. 鍩虹鏈嶅姟

纭锛?
- MySQL 宸插惎鍔?- Redis 宸插惎鍔?- 鍓嶇宸插惎鍔?- 鍚庣宸插惎鍔?
### 3. 缂栬瘧妫€鏌?
寤鸿姣忔杈冨ぇ鏀瑰姩鍚庢墽琛岋細

- 鍚庣锛歚python -m compileall backend`
- 鍓嶇锛歚npm run build`

閫氳繃璇存槑锛?
- 鑷冲皯娌℃湁鏄庢樉璇硶閿欒
- 鍓嶇鍙互姝ｅ父鎵撳寘

---

## 浜屻€佹柊闂讳富閾捐矾妫€鏌?
### 1. 鍒嗙被椤?
楠岃瘉锛?
- 棣栭〉鍒嗙被 tab 姝ｅ父鏄剧ず
- 鍒嗙被鍒囨崲鑳藉埛鏂版柊闂绘祦

### 2. 鏂伴椈璇︽儏

楠岃瘉锛?
- 鐐瑰嚮鏂伴椈鑳借繘鍏ヨ鎯呴〉
- 姝ｆ枃銆佹爣棰樸€佹椂闂淬€侀槄璇婚噺姝ｅ父
- 鐩稿叧鎺ㄨ崘鑳借烦鍒颁笅涓€绡?
### 3. 鏀惰棌 / 鍘嗗彶

楠岃瘉锛?
- 鏀惰棌鏂板 / 鍙栨秷姝ｅ父
- 鍘嗗彶椤佃兘璁板綍鏈€杩戞祻瑙?- 鍒犻櫎鍗曟潯 / 娓呯┖鍏ㄩ儴姝ｅ父

---

## 涓夈€佺紦瀛樹笌鐑妫€鏌?
### 1. 鍒嗙被 / 鍒楄〃缂撳瓨

楠岃瘉鏂瑰紡锛?
- 杩炵画璇锋眰鍒嗙被鎺ュ彛涓ゆ
- 杩炵画璇锋眰鏂伴椈鍒楄〃鎺ュ彛涓ゆ

棰勬湡锛?
- 绗簩娆″懡涓洿蹇?- Redis 鎸傛帀鏃舵帴鍙ｄ粛鑳藉洖婧?MySQL

### 2. 娴忚閲忓閲?
楠岃瘉鏂瑰紡锛?
- 杩炵画鍒锋柊鍚屼竴鏉℃柊闂昏鎯呭娆?
棰勬湡锛?
- 鍓嶇鐪嬪埌鐨?`views` 浼氬闀?- 涓€娈垫椂闂村悗 MySQL 涓殑 `views` 浼氳鍥炲埛琛ラ綈

### 3. 鐑鎺ュ彛

楠岃瘉鏂瑰紡锛?
- 澶氭璁块棶鏌愪竴鏂伴椈
- 鍐嶈姹傦細
  - `GET /api/news/hot?limit=5`
  - `GET /api/news/hot?categoryId=1&limit=5`

棰勬湡锛?
- 鍒氬垰楂橀璁块棶鐨勬柊闂绘帓搴忔洿闈犲墠

---

## 鍥涖€丄I 鍔╂墜鐘舵€佹鏌?
### 1. 鐘舵€佹帴鍙?
璁块棶锛?
- `GET /api/ai/status`
- `GET /api/ai/index/status`

閲嶇偣妫€鏌ュ瓧娈碉細

- `promptVersion`
- `plannerEnabled`
- `localRetrievalLabel`
- `localHybridStrategy`
- `dualRouteFilterStrategy`
- `finalRerankStrategy`
- `vectorRetrievalActive`
- `embeddingConfigured`
- `embeddingConfigMode`
- `indexSyncReady`

濡傛灉褰撳墠鍚戦噺閾捐矾姝ｅ父锛岄鏈熷簲鎺ヨ繎锛?
- `localRetrievalLabel = lexical-plus-qdrant`
- `localHybridStrategy = weighted-rrf`
- `dualRouteFilterStrategy = route-aware-filtering`
- `finalRerankStrategy = plan-aware-cross-source`
- `vectorRetrievalActive = true`
- `embeddingConfigured = true`
- `embeddingConfigMode = explicit` 鎴?`llm-fallback`
- `indexSyncReady = true`

### 2. AI 椤甸《閮ㄧ姸鎬?
鎵撳紑 AI 椤碉紝椤堕儴搴旇兘鐪嬪埌锛?
- `Prompt news-assistant-v6-route-filter-rerank`
- `Planner 宸插紑鍚痐
- `鏈湴寮曟搸 lexical-plus-qdrant`
- `鍚戦噺 宸叉縺娲籤
- `绱㈠紩 鍙悓姝
- `Embedding 鏄惧紡閰嶇疆 / LLM 鍥為€€`
- `鏈湴铻嶅悎 Weighted RRF`
- `鍙岃矾杩囨护 Route-Aware`
- `鏈€缁堟帓搴?Cross-Source`

---

## 浜斻€佸悜閲忕储寮曟鏌?
### 1. 棰勮鍒囧潡

璁块棶锛?
- `GET /api/ai/index/preview/1`

棰勬湡锛?
- 杩斿洖 `chunkCount`
- 鑳界湅鍒?`snippet / text / charCount`

### 2. Dry Run

璇锋眰锛?
`POST /api/ai/index/sync`

```json
{
  "dryRun": true,
  "limit": 5
}
```

棰勬湡锛?
- 杩斿洖澶氬皯鏉℃柊闂汇€佸灏戜釜 chunk
- 涓嶇湡姝ｅ啓鍏ョ储寮?
### 3. 鐪熷疄鍚屾

璇锋眰锛?
```json
{
  "dryRun": false,
  "newsIds": [1, 2, 3]
}
```

棰勬湡锛?
- `status = synced`
- `upsertedPoints` 鏈夊€?- `vectorSize` 鏈夊€?
---

## 鍏€佹湰鍦版绱㈡鏌?
### 1. lexical 妫€绱?
杈撳叆锛?
- 甯︽湁寮哄疄浣撹瘝鐨勯棶棰?- 鐩存帴澶嶈堪鏂伴椈鏍囬鐨勯棶棰?
棰勬湡锛?
- 鏇村鏄撳懡涓湰鍦版柊闂?- 鏉ユ簮鏍囩鏇村鏄撳嚭鐜?`lexical`

### 2. vector 妫€绱?
杈撳叆锛?
- 涓嶇洿鎺ュ杩版爣棰橈紝鑰屾槸鎹竴绉嶈涔夎〃杈?
棰勬湡锛?
- 浠嶇劧鑳藉懡涓浉杩戞柊闂?- 鏉ユ簮鏍囩鍙兘鍑虹幇 `vector`

### 3. local hybrid

杈撳叆锛?
- 鏃㈠寘鍚爣棰樿繎浼硷紝鍙堝寘鍚涔夋敼鍐欑殑闂

棰勬湡锛?
- 鏉ユ簮鏍囩鏇村鏄撳嚭鐜?`lexical+vector`

---

## 涓冦€乀avily 涓庡弻璺绱㈡鏌?
### 1. Tavily 鐘舵€?
濡傛灉閰嶇疆浜?`TAVILY_API_KEY`锛岄鏈燂細

- `webSearchEnabled = true`
- AI 椤垫樉绀?`Tavily 宸插紑鍚痐

### 2. 涓枃 Web Query Rewrite

杈撳叆锛?
- `鍗槦鍙戝皠璁″垝`
- `鏈€杩戝浗闄呮补浠峰彉鍖朻
- `澶фā鍨嬭瀺璧勫姩鎬乣

棰勬湡锛?
- 鍗充究鏄腑鏂囬棶棰橈紝涔熻兘鏇村鏄撴嬁鍒?Web 鏉ユ簮

### 3. 涓夌妫€绱㈣鍒?
娴嬭瘯闂锛?
- `鏍规嵁鏈湴鏂伴椈搴撴€荤粨涓€涓嬬鎶€鐑偣`
  - 棰勬湡锛歚local-first`

- `浠婂ぉ鏈€鏂扮殑鍗槦鍙戝皠璁″垝鏈変粈涔堣繘灞昤
  - 棰勬湡锛歚web-first`

- `鏈€杩戠鎶€鏂伴椈閲屽摢浜涘彉鍖栨渶鍙兘褰卞搷澶фā鍨嬭涓歚
  - 棰勬湡锛歚hybrid`

---

## 鍏€佹渶缁堝洖绛斾笌鏉ユ簮妫€鏌?
姣忔 AI 鍥炵瓟鍚庯紝閲嶇偣鐪嬶細

- 鏄惁杩斿洖 `retrievalPlan`
- 鏄惁杩斿洖 `strategy`
- 鏄惁杩斿洖 `confidence`
- 鏄惁杩斿洖 `sources`
- 鏈湴鏉ユ簮鏄惁鑳借烦璇︽儏椤?- Web 鏉ユ簮鏄惁鑳芥墦寮€澶栭摼

瀵规潵婧愬崱鐗囩壒鍒湅锛?
- 鏃堕棿
- 鍩熷悕
- `lexical / vector / lexical+vector / web`
- 缁煎悎鍒嗘暟

---

## 涔濄€侀棶棰樻帓鏌ユ彁绀?
### 1. `QDRANT_URL` 鐣欑┖

杩欐槸姝ｅ父鐨勶紝琛ㄧず褰撳墠浣跨敤鏈湴 Qdrant 妯″紡锛屼笉褰卞搷鍔熻兘銆?
### 2. `Embedding` 鏄剧ず `LLM 鍥為€€`

璇存槑褰撳墠 embedding 娌℃湁鏄惧紡閰嶇疆锛岃€屾槸娌跨敤浜嗚亰澶╂ā鍨嬮厤缃€?
涓嶆槸閿欒锛屼絾濡傛灉浣犳兂璁╅厤缃洿娓呮锛屽缓璁樉寮忚ˉ涓?`EMBEDDING_*`銆?
### 3. `绱㈠紩 鍙悓姝 浣嗘绱㈡病鍛戒腑

鍏堢‘璁わ細

1. 鏄惁鐪熺殑鎵ц杩?`dryRun=false` 鐨勫悓姝?2. 鎻愰棶鐨勬柊闂绘槸鍚﹀凡缁忚绱㈠紩
3. 鎻愰棶鏄惁鏇村亸 lexical銆乿ector 鎴?Web

### 4. 閲嶅惎鍚庣鍚庣姸鎬佹病鍙?
浼樺厛妫€鏌ワ細

- 淇敼鐨勬槸鏍圭洰褰?`.env`锛屼笉鏄?`.env.example`
- 鍚庣鏄惁鐪熺殑閲嶅惎浜?
---

## 鍗併€佸缓璁洖褰掗『搴?
姣忔澶ф敼鍚庯紝寤鸿鎸夎繖涓『搴忓洖褰掞細

1. `python -m compileall backend`
2. `npm run build`
3. `/api/ai/status`
4. `/api/ai/index/status`
5. `/api/ai/index/preview/1`
6. `/api/ai/index/sync` dry-run
7. `/api/ai/index/sync` 鐪熷疄鍚屾
8. 棣栭〉 / 璇︽儏 / 鏀惰棌 / 鍘嗗彶
9. AI 椤典笁绫婚棶棰橈細
   - local-first
   - hybrid
   - web-first

鎸夎繖濂楅『搴忥紝鍩烘湰鑳芥瘮杈冨揩瀹氫綅鏄細

- 閰嶇疆闂
- 绱㈠紩闂
- 妫€绱㈤棶棰?- 鍓嶇灞曠ず闂

---

## 鍗佷竴銆乂erifier 涓庢姉骞昏妫€鏌?
### 1. 鐘舵€佹帴鍙?
璁块棶锛?
- `GET /api/ai/status`

閲嶇偣纭锛?
- `verifierEnabled = true`
- `verifierStrategy = rule-based-post-verifier`

AI 椤甸《閮ㄥ簲鏄剧ず锛?
- `Verifier Rule-Based`

### 2. 鏃犺瘉鎹嫆绛?
杈撳叆涓€涓湰鍦板拰 Web 閮介毦浠ュ懡涓殑闂銆?
棰勬湡锛?
- `verificationStatus = refused`
- `evidenceLevel = none`
- `guardrailApplied = true`

### 3. 浣庣疆淇″害鍥為€€

杈撳叆涓€涓彧鍛戒腑灏戦噺鏉ユ簮銆佹垨鑰呭彧鏈?1 鏉″急 Web 鏉ユ簮鐨勯棶棰樸€?
棰勬湡锛?
- `verificationStatus = guarded`
- `evidenceLevel = weak`
- `guardrailApplied = true`

骞朵笖鍥炵瓟姝ｆ枃鍓嶉潰浼氬嚭鐜版洿淇濆畧鐨勬彁閱掞紝鑰屼笉鏄洿鎺ョ粰鍑哄己缁撹銆?
### 4. 姝ｅ父閫氳繃

杈撳叆涓€涓潵婧愯緝澶氥€佷笖鏈湴涓?Web 浜掔浉鏀拺鐨勯棶棰樸€?
棰勬湡锛?
- `verificationStatus = accepted`
- `guardrailApplied = false`
- `evidenceLevel = moderate` 鎴?`strong`

---

## 鍗佷簩銆丵uery Analysis 涓?Formatter 妫€鏌?
### 1. 鐘舵€佹帴鍙?
璁块棶锛?
- `GET /api/ai/status`

閲嶇偣纭锛?
- `queryAnalysisEnabled = true`
- `queryAnalysisStrategy = heuristic-query-analysis`
- `responseFormatterEnabled = true`
- `responseFormatterStrategy = evidence-aware-followups`

### 2. AI 椤甸《閮ㄧ姸鎬?
鎵撳紑 AI 椤靛悗锛岄《閮ㄥ簲鍑虹幇锛?
- `Analysis Heuristic`
- `Formatter Follow-Ups`

### 3. 鍥炵瓟鍐呯殑闂鍒嗘瀽

杈撳叆涓夌被闂锛?
- `鏍规嵁鏈湴鏂伴椈搴撴€荤粨涓€涓嬬鎶€鐑偣`
- `浠婂ぉ鏈€鏂扮殑鍗槦鍙戝皠璁″垝鏈変粈涔堣繘灞昤
- `鏈€杩戠鎶€鏂伴椈閲屽摢浜涘彉鍖栨渶鍙兘褰卞搷澶фā鍨嬭涓歚

棰勬湡姣忔潯鍥炵瓟閮借兘鐪嬪埌锛?
- `鎰忓浘`
- `鏃舵晥`
- `鑼冨洿`
- `鍒嗘瀽璇存槑`

### 4. 杩介棶寤鸿

姣忔潯鍥炵瓟搴斿嚭鐜?1 鍒?3 鏉¤拷闂缓璁€?
鐐瑰嚮浠绘剰寤鸿锛岄鏈燂細

- 浼氱洿鎺ュ彂璧锋柊涓€杞璇?- 涓嶉渶瑕佹墜鍔ㄥ鍒跺缓璁枃鏈?
---

## 鍗佷笁銆丼tateful Workflow 涓庢墽琛岃建杩规鏌?
### 1. 鐘舵€佹帴鍙?
璁块棶锛?
- `GET /api/ai/status`

閲嶇偣纭锛?
- `workflowEnabled = true`
- `workflowStyle = stateful-node-pipeline`
- `workflowNodes` 鑷冲皯鍖呭惈锛?  - `query-analysis`
  - `retrieval-planner`
  - `retrieval`
  - `route-filter`
  - `final-rerank`
  - `generator`
  - `verifier`
  - `response-formatter`

### 2. AI 椤甸《閮ㄧ姸鎬?
鎵撳紑 AI 椤碉紝搴旂湅鍒帮細

- `Workflow Stateful`

### 3. 鍥炵瓟鍐呭伐浣滄祦鎽樿

闂换鎰忛棶棰橈紝鍥炵瓟閲屽簲鍑虹幇锛?
- `宸ヤ綔娴侊細query-analysis -> retrieval-planner -> ...`

### 4. 鍥炵瓟鍐呮墽琛岃建杩?
姣忔潯鍥炵瓟搴旂湅鍒拌嫢骞?trace 琛岋紝鑳戒綋鐜版瘡涓妭鐐癸細

- 鍋氫簡浠€涔?- 褰撳墠鐘舵€佹槸 `瀹屾垚 / 淇濇姢 / 鍥為€€`

### 5. 鍦烘櫙宸紓

閲嶇偣瀵规瘮锛?
- 姝ｅ父鍛戒腑鍦烘櫙
- 浣庣疆淇″害鍥為€€鍦烘櫙
- 鏃犺瘉鎹嫆绛斿満鏅?
棰勬湡 trace 涓?`verifier` 鐨勭姸鎬佷細涓嶅悓銆?---

## 鍗佸洓銆丩angSmith SDK Tracing 妫€鏌?### 1. 鐜鍙橀噺

纭鏍圭洰褰?`.env` 涓凡閰嶇疆锛?
- `LANGSMITH_TRACING=true`
- `LANGSMITH_API_KEY=...`
- `LANGSMITH_PROJECT=agentnews-dev`

### 2. 鐘舵€佹帴鍙?
璁块棶锛?
- `GET /api/ai/status`

閲嶇偣纭锛?
- `langsmithReady = true`
- `langsmithSdkInstalled = true`
- `langsmithConfigured = true`

### 3. 瀹為檯闂瓟

鍙戣捣涓€杞?AI 闂瓟鍚庯紝妫€鏌ワ細

- 鍓嶇鍥炵瓟涓湁 `Trace / Run`
- `GET /api/ai/runs/recent` 鏈夋柊璁板綍
- 鏈湴 `agent_runs.jsonl` 鏈夋柊璁板綍
- LangSmith 骞冲彴鑳界湅鍒板搴?trace

---

## 鍗佷簲銆丩angGraph StateGraph 妫€鏌?### 1. 鐜鍙橀噺

纭鏍圭洰褰?`.env` 涓細

- `AGENT_WORKFLOW_ENGINE=langgraph`

### 2. 鐘舵€佹帴鍙?
璁块棶锛?
- `GET /api/ai/status`

閲嶇偣纭锛?
- `workflowEnabled = true`
- `workflowEngine = "langgraph"`
- `workflowStyle = "langgraph-stategraph"`
- `graphVisualizationReady = true`

### 3. AI 椤甸《閮ㄧ姸鎬?
鎵撳紑 AI 椤碉紝椤堕儴搴旂湅鍒帮細

- `Workflow LangGraph`
- `Graph Ready`

### 4. LangSmith 鍥捐鍥?
鍙戣捣涓€杞?AI 闂瓟鍚庯紝鍦?LangSmith 骞冲彴妫€鏌ワ細

- 鏄惁鑳界湅鍒?`AgentNews Workflow`
- 鏄惁鑳界湅鍒拌妭鐐规墽琛岄摼璺?- 鑺傜偣涓簲鍖呭惈锛?  - `query-analysis`
  - `retrieval-planner`
  - `retrieval`
  - `route-filter`
  - `final-rerank`
  - `generator`
  - `verifier`
  - `response-formatter`
  - `no-evidence-response`锛堝湪鏃犺瘉鎹満鏅笅锛?
---

## 鍗佸叚銆乄orkflow Graph Export 妫€鏌?### 1. 鍥剧粨鏋勬帴鍙?
璁块棶锛?
- `GET /api/ai/workflow/graph`

閲嶇偣纭锛?
- `engine = "langgraph"`
- `style = "langgraph-stategraph"`
- `graphVisualizationReady = true`

### 2. 鑺傜偣涓庤竟

杩斿洖閲屽簲鐪嬪埌锛?
- `nodes`
- `edges`
- `mermaid`

鑺傜偣涓簲鑷冲皯鍖呭惈锛?
- `__start__`
- `query-analysis`
- `retrieval-planner`
- `retrieval`
- `route-filter`
- `final-rerank`
- `generator`
- `verifier`
- `response-formatter`
- `no-evidence-response`
- `__end__`

### 3. Mermaid

鎶?`mermaid` 鏂囨湰澶嶅埗鍒版敮鎸?Mermaid 鐨?Markdown 鐜閲岋紝搴旇兘娓叉煋娴佺▼鍥俱€?
---

## 鍗佷竷銆丒valuation Baseline 妫€鏌?### 1. 璇勬祴闆?
璁块棶锛?
- `GET /api/ai/eval/dataset`

搴旂湅鍒伴缃瘎娴嬫牱鏈€?
### 2. 璺戝熀绾胯瘎娴?
璇锋眰锛?
- `POST /api/ai/eval/run`

绀轰緥 body锛?
```json
{
  "limit": 6
}
```

### 3. 缁撴灉瀛楁

閲嶇偣纭锛?
- `plannerAccuracy`
- `intentAccuracy`
- `freshnessAccuracy`
- `scopeAccuracy`
- `results`

### 4. 鍗曟潯 case

姣忎釜 `result` 閲屽簲鍖呭惈锛?
- `actualPlan / expectedPlan`
- `actualIntent / expectedIntent`
- `actualFreshness / expectedFreshness`
- `actualScope / expectedScope`
- `mismatches`

### 5. 鐜褰卞搷

濡傛灉 `TAVILY_API_KEY` 鏈惎鐢紝`webEnabled` 浼氬奖鍝?planner 缁撴灉銆? 
鎵€浠ュ缓璁湪 Tavily 宸插紑鍚殑鐜涓嬭窇杩欑粍 baseline銆?
---

## 鍗佸叓銆丒valuation Feedback Loop 妫€鏌?### 1. 璺戜竴娆¤瘎娴?
璇锋眰锛?
- `POST /api/ai/eval/run`

### 2. 鏌ョ湅鏈€杩戣瘎娴?run

璁块棶锛?
- `GET /api/ai/eval/runs/recent`

搴旂湅鍒帮細

- `runId`
- `recordedAt`
- `totalCount`
- `passedCount`
- `plannerAccuracy`
- `intentAccuracy`
- `freshnessAccuracy`
- `scopeAccuracy`

### 3. 鏌ョ湅鏈€杩戝け璐?case

璁块棶锛?
- `GET /api/ai/eval/failures/recent`

搴旂湅鍒帮細

- `caseId`
- `title`
- `mismatches`
- `expectedPlan / actualPlan`
- `expectedIntent / actualIntent`
- `expectedFreshness / actualFreshness`
- `expectedScope / actualScope`

### 4. LangSmith Evaluation 鐘舵€?
璁块棶锛?
- `GET /api/ai/eval/langsmith/status`

閲嶇偣纭锛?
- `langsmithReady`
- `langsmithConfigured`
- `datasetUploadReady`
- `defaultDatasetName`

### 5. LangSmith Export

璁块棶锛?
- `GET /api/ai/eval/langsmith/export`

搴旂湅鍒帮細

- `datasetName`
- `exampleCount`
- `examples`

### 6. LangSmith Sync

璇锋眰锛?
- `POST /api/ai/eval/langsmith/sync`

濡傛灉褰撳墠 LangSmith 宸查厤缃紝棰勬湡锛?
- `synced = true`
- 杩斿洖 `datasetId`

濡傛灉鏈厤缃紝棰勬湡锛?
- `synced = false`
- `note` 璇存槑褰撳墠浠呮敮鎸佹湰鍦板鍑?
