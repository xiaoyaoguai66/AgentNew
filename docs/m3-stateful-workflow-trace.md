# M3.13 Stateful Workflow 涓庢墽琛岃建杩?
## 杩欎竴闃舵涓轰粈涔堣鍋?
鍒?`M3.12` 涓烘锛岄」鐩凡缁忔湁涓€鏉℃瘮杈冨畬鏁寸殑鍙楁帶閾捐矾锛?
- Query Analysis
- Retrieval Planner
- Retrieval
- Route-Aware Filtering
- Final Rerank
- Generator
- Verifier
- Response Formatter

浣嗚繖浜涜妭鐐硅櫧鐒堕€昏緫涓婂凡缁忓瓨鍦紝浠ｇ爜閲岃繕鏄€滈『搴忚皟涓€涓叉湇鍔♀€濄€?
杩欎細鏈変袱涓棶棰橈細

1. 鍚庨潰濡傛灉鎺?`LangGraph`锛岃繕闇€瑕佸啀閲嶆柊姊崇悊鑺傜偣杈撳叆杈撳嚭
2. 褰撳墠铏界劧鐭ラ亾绯荤粺鈥滃仛浜嗗摢浜涗簨鈥濓紝浣嗙敤鎴峰拰寮€鍙戣€呰繕鐪嬩笉鍒颁竴杞洖绛斿埌搴曡蛋浜嗗摢浜涜妭鐐广€佹瘡姝ヤ骇鍑轰簡浠€涔?
鎵€浠ヨ繖涓€闃舵琛ョ殑鏄細

- `Stateful Workflow`
- `Workflow Trace`

鐩爣鏄绯荤粺浠庘€滄湁鑺傜偣姒傚康鈥濆崌绾ф垚鈥滄湁鐘舵€併€佹湁杞ㄨ抗鐨勮妭鐐瑰伐浣滄祦鈥濄€?
---

## 杩欎竴闃舵鍋氫簡浠€涔?
### 1. 鏂板 Agent Workflow Service

鏂板锛?
- `backend/services/agent_workflow_service.py`

杩欏眰鎶婂綋鍓嶄富閾捐矾鐪熸鏀跺彛鎴愪竴涓姸鎬佸寲宸ヤ綔娴併€?
褰撳墠娴佺▼鍙樻垚锛?
```text
query-analysis
-> retrieval-planner
-> retrieval
-> route-filter
-> final-rerank
-> generator
-> verifier
-> response-formatter
```

姣忎釜鑺傜偣鎵ц鏃讹紝閮戒細鎶婄粨鏋滃啓鍥炵粺涓€鐨?workflow state銆?
### 2. 鏂板 Workflow State

杩欎竴姝ユ柊澧炰簡涓€涓唴閮ㄧ殑 `WorkflowState`锛岀粺涓€淇濆瓨锛?
- query analysis 缁撴灉
- retrieval planner 鍐崇瓥
- local / web sources
- merged sources
- confidence
- verification result
- follow-up suggestions
- workflow trace

杩欎竴姝ョ殑浠峰€煎緢楂橈紝鍥犱负瀹冩剰鍛崇潃锛?
**绯荤粺涓嶅啀鍙槸鈥滄墽琛屼簡涓€鍫嗗嚱鏁扳€濓紝鑰屾槸鈥滃洿缁曚竴浠界姸鎬侀€愭鎺ㄨ繘鈥濄€?*

### 3. 鏂板 Workflow Trace

鍚庣鐜板湪浼氫负姣忎竴杞璇濊褰曟墽琛岃建杩癸紝姣忎釜鑺傜偣閮戒細浜у嚭锛?
- `stepIndex`
- `node`
- `status`
- `detail`
- `durationMs`

涔熷氨鏄锛岀郴缁熶笉鍙煡閬撴渶鍚庡洖绛旀槸浠€涔堬紝杩樿兘鍛婅瘔浣狅細

- 鍏堝仛浜嗛棶棰樺垎鏋?- 鍐冲畾浜嗗摢绉嶆绱㈣鍒?- 妫€绱㈠埌浜嗗灏戞湰鍦板拰 Web 鏉ユ簮
- rerank 鍚庝繚鐣欎簡澶氬皯鏉ユ簮
- verifier 鏄甯搁€氳繃杩樻槸瑙﹀彂浜嗕繚鎶?
### 4. 鍝嶅簲涓柊澧?Workflow 淇℃伅

`AiChatResponse` 鐜板湪鏂板锛?
- `workflowSummary`
- `workflowTrace`

鍓嶇 AI 椤典篃浼氭樉绀猴細

- 椤堕儴鐘舵€侊細`Workflow Stateful`
- 姣忔潯鍥炵瓟鐨勫伐浣滄祦鎽樿
- 姣忎釜鑺傜偣鐨勬墽琛岃建杩?
杩欎竴姝ヨ绯荤粺浠庘€滈粦鐩掓墽琛屸€濆彉鎴愨€滃彲瑙傚療宸ヤ綔娴佲€濄€?
---

## 鎶€鏈悕璇嶈В閲?
### 1. Stateful Workflow

`Stateful Workflow` 鎸囩殑鏄細

**姣忎釜鑺傜偣涓嶆槸鍚勭畻鍚勭殑锛岃€屾槸鍥寸粫鍚屼竴浠界姸鎬侀€愭鏇存柊銆?*

杩欏拰绠€鍗曠殑鍑芥暟涓茶璋冪敤涓嶄竴鏍枫€?
鍑芥暟涓茶璋冪敤閫氬父鏄細

- 涓婁竴姝ヨ繑鍥炰粈涔堬紝涓嬫灏辨帴浠€涔?
鑰岀姸鎬佸寲宸ヤ綔娴佹槸锛?
- 鏁翠釜娴佺▼鍥寸粫涓€浠界粺涓€鐘舵€佹帹杩?- 姣忎釜鑺傜偣淇敼鎴栬ˉ鍏呭叾涓竴閮ㄥ垎

杩欐洿閫傚悎鍚庨潰杩佺Щ鍒?`LangGraph` 杩欑鍥惧紡缂栨帓妗嗘灦銆?
### 2. Workflow Trace

`Workflow Trace` 鎸囩殑鏄細

**鎶婃瘡涓妭鐐圭殑鎵ц杞ㄨ抗鏄惧紡璁板綍涓嬫潵銆?*

瀹冪殑浣滅敤鍖呮嫭锛?
- 璋冭瘯
- 婕旂ず
- 瑙傛祴
- 闈㈣瘯璁茶В

褰撳墠 trace 閲屾瘡涓€姝ラ兘浼氬甫锛?
- 鑺傜偣鍚?- 鑺傜偣鐘舵€?- 鑺傜偣璇存槑
- 鑰楁椂

### 3. LangGraph-ready

杩欓噷璇寸殑 `LangGraph-ready`锛屼笉鏄凡缁忔寮忔帴鍏ヤ簡 LangGraph锛岃€屾槸锛?
**褰撳墠鑺傜偣鍜岀姸鎬佸凡缁忔寜鍥剧紪鎺掓€濈淮鎷嗗ソ浜嗐€?*

鍚庨潰濡傛灉浣犳帴 LangGraph锛屼富瑕佸仛鐨勬槸锛?
- 鎶婂綋鍓嶈妭鐐规敞鍐屾垚 graph node
- 鎶婂綋鍓?state 杩佹垚 graph state
- 鎶婂綋鍓?trace 鎺ュ叆鍥剧骇瑙傛祴

鑰屼笉鏄粠闆舵帹缈婚噸鍐欍€?
---

## 涓轰粈涔堣繖涓€姝ラ噸瑕?
杩欎竴闃舵瀵归潰璇曚环鍊奸潪甯搁珮锛屽洜涓哄畠鎶婁綘鐨勭郴缁熶粠锛?
```text
鑳藉洖绛旈棶棰?```

鍗囩骇鎴愪簡锛?
```text
鏈夌姸鎬佸伐浣滄祦
+ 鏈夎妭鐐硅竟鐣?+ 鏈夋墽琛岃建杩?+ 鍙户缁縼绉诲埌 LangGraph
```

杩欐剰鍛崇潃浣犲悗闈㈠彲浠ユ洿鑷劧鍦板洖绛旓細

- 涓轰粈涔堥€傚悎杩佸埌 LangGraph
- LangGraph 涔嬪墠浣犲仛浜嗗摢浜涘噯澶?- 浣犵幇鍦ㄧ殑宸ヤ綔娴佽妭鐐规槸浠€涔?- 浣犲浣曡娴嬫瘡涓€杞?Agent 鎵ц

---

## 鎬庝箞娴嬭瘯

### 1. 鐪嬬姸鎬佹帴鍙?
璁块棶锛?
- `GET /api/ai/status`

鏂板瀛楁棰勬湡锛?
- `workflowEnabled = true`
- `workflowStyle = stateful-node-pipeline`
- `workflowNodes` 鍖呭惈 8 涓妭鐐?
### 2. 鐪?AI 椤甸《閮ㄧ姸鎬?
鎵撳紑 AI 椤碉紝椤堕儴搴旀柊澧烇細

- `Workflow Stateful`

### 3. 鐪嬫瘡鏉″洖绛旂殑 Workflow Summary

闂换鎰忎竴涓棶棰樺悗锛屽洖绛旈噷搴斿嚭鐜帮細

- `宸ヤ綔娴侊細query-analysis -> retrieval-planner -> ...`

### 4. 鐪?Workflow Trace

姣忔潯鍥炵瓟涓嬫柟搴斿嚭鐜拌妭鐐硅建杩癸紝渚嬪锛?
- 闂鍒嗘瀽
- 妫€绱㈣鍒?- 妫€绱㈡墽琛?- 鍙岃矾杩囨护
- 鏈€缁堟帓搴?- 鍥炵瓟鐢熸垚
- 鍥炵瓟鏍￠獙
- 杈撳嚭鏁寸悊

### 5. 鐪嬩笉鍚屽満鏅笅鐨?trace 鏄惁鍙樺寲

渚嬪锛?
- 鏃犺瘉鎹満鏅簲鏇村鏄撳嚭鐜?verifier 鐨?`fallback`
- 浣庣疆淇″害鍦烘櫙 verifier 搴旀槸 `guarded`
- 姝ｅ父鍦烘櫙 verifier 搴旀槸 `completed`

---

## 鍜屽悗缁?LangGraph / LangSmith 鐨勫叧绯?
杩欎竴姝ヤ箣鍚庯紝绯荤粺宸茬粡鏈変簡锛?
- state
- nodes
- trace

鍥犳鍚庨潰鏃犺浣犳槸锛?
- 鎺?`LangGraph`
- 鎺?`LangSmith` 椋庢牸鐨?trace 瑙傛祴
- 鍋氱绾胯瘎娴嬮泦

閮戒細姣旂洿鎺ュ湪涓€涓插嚱鏁拌皟鐢ㄤ笂纭帴鏇磋嚜鐒躲€?
鎵€浠?`M3.13` 鐨勬剰涔変笉鏄€滃姞浜嗕釜 trace 闈㈡澘鈥濓紝鑰屾槸锛?
**鎶婂綋鍓?Agent 鐪熸鏀跺彛鎴愪簡 LangGraph-ready 鐨勭姸鎬佸寲宸ヤ綔娴併€?*

