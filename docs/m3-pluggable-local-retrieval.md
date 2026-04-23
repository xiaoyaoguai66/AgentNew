# M3.6 鍙彃鎷旀湰鍦版绱㈠眰锛氫负 Qdrant 鎺ュ叆鍋氬噯澶?
## 杩欎竴闃舵涓轰粈涔堣鍋?
鍒?`M3.5` 涓烘锛屾柊闂诲姪鎵嬪凡缁忓叿澶囷細

- `Retrieval Planner`
- 鏈湴鏂伴椈 lexical baseline
- Tavily Web Search
- Query Rewrite
- Fusion + 杞婚噺 rerank

浣嗘湰鍦版绱㈠眰杩樻湁涓€涓槑鏄鹃棶棰橈細

**褰撳墠鏈湴妫€绱㈠彧鏈変竴濂楀疄鐜帮紝鑰屼笖鍏ュ彛鍜屽疄鐜版槸缁戝畾鍦ㄤ竴璧风殑銆?*

杩欎細甯︽潵涓や釜鍚庣画闂锛?
1. 涓€鏃︽帴 `Qdrant`锛屽氨瑕佺洿鎺ユ敼鍐欑幇鏈夋湰鍦版绱富閾捐矾  
   杩欎細璁?`M3.3 ~ M3.5` 閲屽凡缁忕ǔ瀹氫笅鏉ョ殑 Planner銆丗usion 鍜?AI 涓绘祦绋嬮噸鏂版壙鍙楁敼鍔ㄩ闄┿€?
2. 闈㈣瘯鏃跺緢闅炬妸鈥滄柟娉曟紨杩涒€濊娓呮  
   濡傛灉浠ｇ爜閲屽彧鏈変竴涓?`news_retrieval_service.py`锛屽緢闅炬竻鏅拌鏄庯細
   - 褰撳墠鐢ㄧ殑鏄?lexical baseline
   - 鍚庨潰鍑嗗鎬庝箞鎺ュ悜閲忔绱?   - 涓轰粈涔堣鍏堝仛 abstraction 鍐嶄笂 Qdrant

鎵€浠?`M3.6` 鐨勭洰鏍囦笉鏄珛鍒绘妸鍚戦噺妫€绱㈠叏鍋氬畬锛岃€屾槸锛?
**鍏堟妸鏈湴妫€绱㈠仛鎴愬彲鎻掓嫈缁撴瀯锛岃 lexical baseline 鍜屽悗缁?Qdrant 闆嗘垚鏈夌ǔ瀹氭帴鍙ｃ€?*

---

## 杩欎竴闃舵瑙ｅ喅浜嗕粈涔?
鏈鏀归€犲悗锛屾湰鍦版绱㈠眰浠庘€滃崟鏂囦欢瀹炵幇鈥濆崌绾ф垚浜嗕笁灞傜粨鏋勶細

1. `lexical_news_retriever.py`
   - 淇濈暀骞舵壙鎺ュ綋鍓嶅彲杩愯鐨?lexical baseline

2. `vector_news_retriever.py`
   - 浣滀负 Qdrant / vector retrieval 鐨勯鐣欏疄鐜板叆鍙?
3. `news_retrieval_service.py`
   - 浣滀负缁熶竴鐨勬湰鍦版绱?fa莽ade
   - 鐢卞畠鍐冲畾褰撳墠浣跨敤鍝鏈湴寮曟搸

杩欐牱鍋氫互鍚庯細

- Agent 涓婚摼璺彧渚濊禆 `news_retrieval_service.retrieve_news_sources()`
- 鍏蜂綋鏄?lexical 杩樻槸鍚庣画 vector锛屼笉浼氬啀娉勬紡鍒版洿涓婂眰
- 鍚庨潰鎺?Qdrant 鏃讹紝涓昏鏀瑰姩浼氳闄愬埗鍦ㄦ湰鍦版绱㈠眰鍐呴儴

---

## 鏈浠ｇ爜缁撴瀯鍙樺寲

鏂板锛?
- `backend/services/lexical_news_retriever.py`
- `backend/services/vector_news_retriever.py`

閲嶆瀯锛?
- `backend/services/news_retrieval_service.py`

鍏朵腑鑱岃矗鍒掑垎濡備笅锛?
### 1. lexical_news_retriever.py

杩欓噷鎵挎帴浜嗕綘褰撳墠宸茬粡楠岃瘉杩囩殑鏈湴妫€绱?baseline锛?
- MySQL 鍊欓€夐泦
- 绫诲埆杩囨护
- 鏃堕棿鑼冨洿杩囨护
- lexical 鎵撳垎
- snippet 鎶藉彇

涔熷氨鏄锛?
**褰撳墠鐪熸璺戝湪绾夸笂鐨勬湰鍦版绱紝浠嶇劧鏄繖鏉?lexical baseline銆?*

杩欒兘淇濊瘉锛?
- 褰撳墠鍔熻兘涓嶅洖閫€
- 涔嬪墠鐨勮皟浼橀€昏緫涓嶄涪
- 鏈湴 grounded QA 浠嶇劧淇濇寔绋冲畾

### 2. vector_news_retriever.py

杩欎竴灞傜幇鍦ㄧ殑瀹氫綅涓嶆槸鈥滃凡缁忓畬鎴愬悜閲忔绱⑩€濓紝鑰屾槸锛?
**棰勭暀缁熶竴鐨?vector retrieval 鎺ュ彛锛屽苟鎶婅繍琛屾椂鐘舵€佹樉寮忓寲銆?*

褰撳墠瀹冧細杈撳嚭锛?
- `vectorRetrievalEnabled`
- `vectorStoreConfigured`
- `vectorBackend`
- `vectorRetrievalActive`

鑰岀湡姝ｇ殑鍚戦噺鍙洖閫昏緫鏆傛椂杩樻病鏈夋帴鍏ワ紝鍘熷洜寰堟槑纭細

- 杩樻病鏈夋柊闂?chunk embedding 娴佺▼
- 杩樻病鏈夊悜閲忕储寮曟瀯寤烘祦绋?- 杩樻病鏈夋寮忕殑 Qdrant 鏌ヨ閾捐矾

鎵€浠ヨ繖涓€灞傜洰鍓嶆槸鈥渧ector-ready鈥濓紝涓嶆槸鈥渧ector-complete鈥濄€?
杩欎篃鏄繖涓€姝ヨ璁′笂鏈€閲嶈鐨勫湴鏂癸細

**鍏堟妸鎺ュ彛鍜岀姸鎬佽竟鐣屾惌濂斤紝鍐嶆妸鐪熸鐨勫悜閲忔绱㈠～杩涘幓銆?*

### 3. news_retrieval_service.py

杩欎竴灞傜幇鍦ㄥ彉鎴愪簡鏈湴妫€绱㈡€诲叆鍙ｃ€?
瀹冭礋璐ｏ細

- 瑙ｆ瀽褰撳墠鏈湴妫€绱㈠紩鎿庨厤缃?- 缁熶竴杈撳嚭鏈湴妫€绱㈣繍琛屾椂鐘舵€?- 榛樿璧?lexical baseline
- 鍦?`hybrid-ready` 妯″紡涓嬶紝涓哄悗缁悜閲忔绱㈣瀺鍚堥鐣欒矾寰?
褰撳墠鏀寔鐨勬湰鍦板紩鎿庨厤缃細

- `LOCAL_RETRIEVAL_ENGINE=lexical`
- `LOCAL_RETRIEVAL_ENGINE=hybrid-ready`

鍚箟鏄細

- `lexical`
  - 鍙敤褰撳墠宸茬ǔ瀹氱殑 lexical baseline

- `hybrid-ready`
  - 淇濇寔 lexical 鍙敤
  - 鍚屾椂鎵撳紑鈥滄湭鏉ュ彲浠ュ苟鍏?vector sources鈥濈殑浠ｇ爜缁撴瀯

---

## 涓轰粈涔堣繖涓€姝ヤ笉鐩存帴鎶?Qdrant 鍏ㄦ帴瀹?
鍘熷洜涓嶆槸鈥滀笉鑳藉仛鈥濓紝鑰屾槸鈥滅幇鍦ㄨ繖鏍锋洿鍚堢悊鈥濄€?
Qdrant 鐪熸鎺ュ叆鑷冲皯杩橀渶瑕佽ˉ榻愪笅闈㈠嚑灞傦細

1. 鏂伴椈鍒?chunk
2. embedding 鐢熸垚
3. 寤虹储寮?/ upsert
4. metadata 璁捐
5. 鏌ヨ鎺ュ彛
6. 鍚戦噺鍙洖缁撴灉鍜屽綋鍓?lexical 缁撴灉鐨勬湰鍦拌瀺鍚?
濡傛灉杩欎簺杩樻病鍑嗗濂斤紝灏辩洿鎺ユ妸 Qdrant 寮烘帴杩涘綋鍓嶄富閾捐矾锛屼細鍑虹幇涓や釜闂锛?
- 浠ｇ爜閲屼細鍏呮弧鍗婃垚鍝侀€昏緫
- 闈㈣瘯鏃朵篃寰堥毦璇存竻妤氣€滃綋鍓嶅埌搴曟帴鍒颁簡鍝竴姝モ€?
鍥犳杩欎竴姝ョ殑宸ョ▼绛栫暐鏄細

**鍏堟妸缁撴瀯鎶借薄鍒颁綅锛屽啀璁?Qdrant 鐪熸鎺ュ叆銆?*

杩欐瘮鎶婁竴涓€滆繕娌″缓绔?embedding/index pipeline鈥濈殑鍚戦噺搴撶‖濉炶繘涓绘祦绋嬫洿绋炽€?
---

## 閰嶇疆灞備篃涓€璧峰噯澶囧ソ浜?
杩欐杩樻妸鍚庣画 Qdrant 鍜?embedding 鐩稿叧閰嶇疆琛ヨ繘浜嗭細

- `LOCAL_RETRIEVAL_ENGINE`
- `ENABLE_VECTOR_RETRIEVAL`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION`
- `QDRANT_TIMEOUT_SECONDS`
- `EMBEDDING_BASE_URL`
- `EMBEDDING_API_KEY`
- `EMBEDDING_MODEL`

杩欎簺閰嶇疆鐜板湪宸茬粡杩涘叆锛?
- `backend/config/settings.py`
- `.env.example`

鎰忎箟鍦ㄤ簬锛?
1. 鍚庨潰鎺?Qdrant 鏃朵笉闇€瑕佸啀閲嶆瀯閰嶇疆绯荤粺
2. 杩愯鏃剁姸鎬佽兘澶熸槑纭煡閬擄細
   - 鏈夋病鏈夋墦寮€鍚戦噺妫€绱㈠紑鍏?   - Qdrant 鏄惁宸查厤缃?   - 褰撳墠鏄笉鏄彧鏄?`reserved / ready` 鐘舵€?
---

## 鍓嶇涓轰粈涔堜篃瑕佹樉绀鸿繖浜涚姸鎬?
杩欐鎴戣繕鎶婅繍琛屾椂鐘舵€侀€忓埌浜?`/api/ai/status`锛屽苟鍦?AI 椤靛姞浜嗕袱涓柊鐘舵€侊細

- `鏈湴寮曟搸`
- `鍚戦噺`

杩欎欢浜嬬湅璧锋潵鍍忊€滆皟璇?UI鈥濓紝浣嗗叾瀹炲椤圭洰寰堥噸瑕併€?
鍘熷洜鏄細

1. 浣犺嚜宸辫皟璇曟椂鑳界珛鍒荤湅鍒板綋鍓嶆槸涓嶆槸杩樺湪 lexical baseline
2. 鍚庨潰鎺?Qdrant 鍚庯紝椤甸潰涓婅兘鐩存帴浣撶幇鈥滃綋鍓嶅凡缁忓垏鍒颁簡 vector-ready / vector-active鈥?3. 闈㈣瘯鏃跺彲浠ョ洿鎺ュ睍绀猴細杩欎釜绯荤粺涓嶆槸闈欐€佸啓姝伙紝鑰屾槸鑳借瀵熷綋鍓嶆绱㈡爤鐘舵€?
---

## 杩欎竴姝ュ湪鏂规硶婕旇繘閲岀殑鎰忎箟

杩欎竴姝ラ潪甯搁€傚悎浣犲悗闈㈠湪闈㈣瘯閲岃В閲婏細

鈥滄垜娌℃湁鍦?lexical baseline 杩樻病绋冲畾鐨勬椂鍊欏氨鐩存帴寮轰笂鍚戦噺搴擄紝鑰屾槸鍏堟妸鏈湴妫€绱㈠眰鍋氭垚鍙彃鎷旂粨鏋勩€傝繖鏍峰綋鍓嶇郴缁熺户缁ǔ瀹氳繍琛岋紝鍚庣画鎺?Qdrant 鍙渶瑕佸湪 retriever 灞傚唴閮ㄨˉ chunk銆乪mbedding 鍜屽悜閲忔煡璇紝涓嶉渶瑕佹妸 Planner銆丗usion 鍜?grounded answer 鍏ㄩ儴閲嶅啓銆傗€?

杩欏彞璇濈殑浠峰€煎緢楂橈紝鍥犱负瀹冧綋鐜扮殑鏄細

- 缁撴瀯婕旇繘鎰忚瘑
- 鍙淮鎶ゆ€ф剰璇?- 瀵逛腑闂存€佹柟妗堢殑宸ョ▼鎺у埗

---

## 褰撳墠鐘舵€佽璇村噯纭?
杩欎竴闃舵瀹屾垚鍚庯紝鏈€鍑嗙‘鐨勬弿杩版槸锛?
- 褰撳墠绾夸笂鏈湴妫€绱㈠紩鎿庯細`lexical baseline`
- 褰撳墠绯荤粺缁撴瀯锛歚vector-ready`
- 褰撳墠鍚戦噺妫€绱㈢姸鎬侊細`鎺ュ彛鍜岄厤缃凡棰勭暀锛屼絾 Qdrant + embedding pipeline 杩樻病姝ｅ紡鎺ュ叆`

涓嶈鎶婅繖涓€姝ヨ鎴愨€滃凡缁忓畬鎴愪簡鍚戦噺妫€绱⑩€濓紝閭ｆ牱浼氬湪闈㈣瘯閲岃闂┛銆?
姝ｇ‘璇存硶搴旇鏄細

**鈥滄垜鍏堟妸鏈湴妫€绱㈠眰鍋氭垚浜嗗彲鎻掓嫈鏋舵瀯锛屼繚鎸?lexical baseline 鎸佺画鍙敤锛屽悓鏃朵负 Qdrant 鎺ュ叆棰勭暀浜嗙嫭绔?vector retriever 鍜岃繍琛屾椂閰嶇疆銆傗€?*

---

## 鎵嬪姩娴嬭瘯寤鸿

浣犵幇鍦ㄥ彲浠ヨ繖鏍烽獙璇佽繖涓€闃舵锛?
1. 姝ｅ父鍚姩鍓嶅悗绔?2. 鎵撳紑 AI 椤?3. 鏌ョ湅椤堕儴鐘舵€侊細
   - `鏈湴寮曟搸` 榛樿搴旀樉绀?`lexical-baseline`
   - `鍚戦噺` 榛樿搴旀樉绀?`鏈紑鍚痐
4. 濡傛灉浣犲湪 `.env` 閲岃缃細
   - `LOCAL_RETRIEVAL_ENGINE=hybrid-ready`
   - `ENABLE_VECTOR_RETRIEVAL=true`
   - 浣嗕笉閰嶇疆 `QDRANT_URL`
   閭ｅ墠绔簲鏄剧ず锛?   - `鏈湴寮曟搸` 鍙樻垚 `lexical-plus-vector-ready`
   - `鍚戦噺` 鍙樻垚 `寮€鍏冲凡寮€锛岀储寮曟湭閰峘
5. 鍦ㄨ繖涓ょ妯″紡涓嬬户缁彁闂紝褰撳墠鍥炵瓟鑳藉姏涓嶅簲鍥為€€锛屽洜涓?lexical baseline 浠嶇劧鏄粯璁や富閾捐矾

---

## 涓嬩竴姝ユ€庝箞鎺?Qdrant

鏈変簡杩欎竴灞?abstraction锛屼笅涓€姝ュ氨鍙互姝ｅ紡鎺ㄨ繘锛?
1. 鏂伴椈 chunk 璁捐
2. embedding 鐢熸垚閾捐矾
3. Qdrant upsert / 绱㈠紩鍒濆鍖?4. metadata filter
5. vector retrieval 鍜?lexical retrieval 鐨勬湰鍦版贩鍚堝彫鍥?
涔熷氨鏄锛屼粠杩欎竴闃舵寮€濮嬶紝鍚庣画鐨?Qdrant 鎺ュ叆缁堜簬鑳藉彉鎴愶細

**鍦ㄧǔ瀹氭帴鍙ｉ噷濉疄鐜帮紝鑰屼笉鏄帹缈荤幇鏈夌粨鏋勩€?*

