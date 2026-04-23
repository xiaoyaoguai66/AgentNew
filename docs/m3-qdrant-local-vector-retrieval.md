# M3.8 Qdrant 鏈湴鍚戦噺妫€绱細鎶?vector-ready 鍙樻垚鐪熸鍙敤鐨勬湰鍦板彫鍥?
## 杩欎竴闃舵鍋氫簡浠€涔?
杩欎竴闃舵鎶?`M3.6` 鍜?`M3.7` 閲屽凡缁忛鐣欏ソ鐨勫悜閲忔绱㈢粨鏋勶紝鐪熸琛ユ垚浜嗗彲杩愯閾捐矾锛?
1. 瀹夎骞舵帴鍏?`qdrant-client`
2. 璁╁悗绔敮鎸?`Qdrant local persistent mode`
3. 鎵撻€?`鏂伴椈鍒囧潡 -> embedding -> collection -> upsert -> query` 鍏ㄦ祦绋?4. 璁?`vector_news_retriever` 涓嶅啀鍙槸棰勭暀鎺ュ彛锛岃€屾槸鑳借繑鍥炵湡瀹炲悜閲忓彫鍥炵粨鏋?5. 淇濇寔鐜版湁 lexical baseline 缁х画鍙敤锛屽苟鍦?`hybrid-ready` 妯″紡涓嬪拰鍚戦噺缁撴灉铻嶅悎

涔熷氨鏄锛屽埌杩欎竴闃舵涓烘锛岄」鐩噷鐨勬湰鍦版绱㈠凡缁忎笉鍐嶅彧鏄細

- lexical baseline

鑰屾槸鍗囩骇鎴愪簡锛?
- lexical baseline
- Qdrant 鏈湴鍚戦噺鍙洖
- 涓よ€呭彲鎻掓嫈銆佸彲铻嶅悎

---

## 涓轰粈涔堣繖涓€姝ヨ繖鏍峰仛

### 1. 涓轰粈涔堜笉鏄洿鎺ヤ笂 Docker 鐗?Qdrant

鐞嗘兂鎯呭喌涓嬶紝浼佷笟鐜閫氬父浼氭妸 Qdrant 浣滀负鐙珛鏈嶅姟杩愯銆?
浣嗗綋鍓嶆湰鍦扮幆澧冮噷锛孌ocker daemon 涓嶅彲鐢紝鎵€浠ヨ繖涓€姝ユ病鏈夊己琛岃姹傚厛鎶婂鍣ㄩ摼璺窇閫氾紝鑰屾槸閫夋嫨浜?`qdrant-client` 鑷甫鐨勬湰鍦版寔涔呭寲妯″紡銆?
杩欐牱鍋氱殑鍘熷洜寰堢幇瀹烇細

1. 鍏堟妸鈥滃悜閲忔绱富鑳藉姏鈥濊窇閫?2. 閬垮厤琚湰鍦?Docker 鐜鍗′綇鏁存潯鐮斿彂璺緞
3. 鍚庣画濡傛灉闇€瑕佸垏鍒扮嫭绔?Qdrant 鏈嶅姟锛屽彧闇€瑕佹敼閰嶇疆锛屼笉闇€瑕佹帹缈诲綋鍓嶆绱㈢粨鏋?
鎵€浠ヨ繖涓€姝ョ殑宸ョ▼绛栫暐鏄細

**鍏堢敤 Qdrant local mode 璺戦€氱湡瀹炲悜閲忔绱紝鍐嶄繚鐣欏悗缁垏鍒版湇鍔″寲閮ㄧ讲鐨勭┖闂淬€?*

### 2. 涓轰粈涔堜笉鏄寜鏂伴椈绫诲埆閫変笉鍚?embedding

褰撳墠娌℃湁鎸夆€滅鎶€ / 璐㈢粡 / 鍥介檯鈥濆垎鍒€変笉鍚?embedding 妯″瀷锛岃€屾槸鍧氭寔涓€濂楃粺涓€鐨?retrieval embedding銆?
鍘熷洜鏄細

1. 妫€绱㈡椂锛宍query` 鍜?`document chunk` 蹇呴』鍦ㄥ悓涓€涓悜閲忕┖闂撮噷姣旇緝
2. 鏂伴椈鍒嗙被杩囨护鏇撮€傚悎浜ょ粰 metadata filter锛岃€屼笉鏄媶鎴愬濂?embedding 妯″瀷
3. 澶氭ā鍨嬩細璁╃储寮曠淮鎶ゃ€佸彫鍥炲榻愬拰闈㈣瘯瑙ｉ噴閮藉彉澶嶆潅

鎵€浠ュ綋鍓嶆洿鍚堢悊鐨勬柟妗堟槸锛?
- 涓€濂楃粺涓€ embedding
- `category / publish_time / source` 杩欎簺淇℃伅璧?payload filter
- 鏈€缁堟帓搴忓啀缁撳悎 lexical / rerank 澶勭悊

### 3. 涓轰粈涔堣繖涓€闃舵淇濈暀 lexical baseline

鍥犱负鍚戦噺妫€绱笉鏄潵鈥滄浛鎹㈡墍鏈変笢瑗库€濈殑锛岃€屾槸鏉ヨˉ lexical retrieval 鐨勭煭鏉裤€?
鏂伴椈鍦烘櫙閲岋細

- `lexical retrieval` 鎿呴暱鍛戒腑瀹炰綋璇嶃€佹爣棰樿瘝銆佹斂绛栧悕銆佸叕鍙稿悕
- `vector retrieval` 鎿呴暱璇箟鐩歌繎銆佽〃杈炬敼鍐欍€佹ā绯婃彁闂?
鎵€浠ユ洿閫傚悎鏂伴椈椤圭洰鐨勶紝涓嶆槸鈥滃彧淇濈暀涓€涓€濓紝鑰屾槸锛?
**lexical + vector 鐨勬贩鍚堟绱€?*

---

## 杩欎竴姝ユ秹鍙婄殑鎶€鏈悕璇嶆槸浠€涔堟剰鎬?
### 1. Chunk

`chunk` 灏辨槸鎶婁竴绡囧畬鏁存柊闂绘媶鎴愬娈靛悗锛屾瘡涓€娈靛舰鎴愮殑鏈€灏忔绱㈠崟鍏冦€?
涓轰粈涔堣鎷嗭細

- 涓€鏁寸瘒鏂伴椈鐩存帴鍋氬悜閲忥紝绮掑害澶矖
- 鐢ㄦ埛闂閫氬父鍙搴旀鏂囬噷鐨勬煇涓€閮ㄥ垎
- chunk 杩樿兘鏂逛究鍚庣画鍋氭潵婧愬紩鐢ㄥ拰 snippet 灞曠ず

褰撳墠椤圭洰閲岋紝鏂伴椈鍒囧潡绛栫暐鏄細

- 鏍囬鍜屾憳瑕佸寮?- 娈佃惤浼樺厛
- 鍥哄畾瀛楃绐楀彛
- overlap 闃叉杈圭晫淇℃伅琚垏鏂?
### 2. Embedding

`embedding` 鍙互鐞嗚В鎴愨€滄妸鏂囨湰鍙樻垚涓€涓查珮缁存暟瀛楀悜閲忊€濓紝杩欐牱绯荤粺灏辫兘姣旇緝涓ゆ鏂囨湰鍦ㄨ涔変笂鐨勬帴杩戠▼搴︺€?
杩欎竴姝ュ仛鐨勪笉鏄垎绫伙紝鑰屾槸涓轰簡妫€绱細

- 鐢ㄦ埛闂鍏堣浆鎴愬悜閲?- 鏂伴椈 chunk 涔熻浆鎴愬悜閲?- 鍐嶅湪鍚戦噺搴撻噷鎵锯€滄渶鎺ヨ繎鈥濈殑 chunk

### 3. Collection

`collection` 鏄?Qdrant 閲岀殑鈥滃悜閲忛泦鍚堚€濄€?
浣犲彲浠ユ妸瀹冪悊瑙ｆ垚锛?
- 涓€涓笓闂ㄥ瓨鏂伴椈 chunk 鍚戦噺鐨勮〃
- 浣嗗畠涓嶅彧瀛樺悜閲忥紝涔熷瓨姣忎釜鐐圭殑鍏冩暟鎹?
褰撳墠榛樿 collection 鏄細

- `agentnews_news_chunks`

### 4. Payload

`payload` 灏辨槸璺熺潃鍚戦噺涓€璧峰瓨杩涘幓鐨勫厓鏁版嵁銆?
褰撳墠椤圭洰閲屼富瑕佸寘鎷細

- `news_id`
- `chunk_id`
- `chunk_index`
- `title`
- `snippet`
- `chunk_text`
- `category_id`
- `publish_time`
- `publish_timestamp`
- `author`

杩欎簺瀛楁寰堥噸瑕侊紝鍥犱负鍚庨潰妫€绱笉鍙槸鈥滅浉浼煎害鏈€楂樷€濓紝杩樿鏀寔锛?
- 鍒嗙被杩囨护
- 鏃堕棿鑼冨洿杩囨护
- 鏉ユ簮灞曠ず
- 鐐瑰嚮鏉ユ簮璺虫柊闂昏鎯?
### 5. Local Persistent Mode

杩欐槸杩欎竴姝ヤ笓闂ㄩ€夌敤鐨?Qdrant 杩愯鏂瑰紡銆?
瀹冪殑鍚箟鏄細

- Qdrant 涓嶅崟鐙捣涓€涓繙绋嬫湇鍔?- 鑰屾槸鎶婄储寮曠洿鎺ユ寔涔呭寲鍒版湰鍦扮洰褰?- 褰撳墠鐩綍榛樿鏄?`backend/data/qdrant`

浼樼偣锛?
- 鏈湴寮€鍙戠畝鍗?- 涓嶉渶瑕佸厛閰嶆湇鍔＄
- 鐪熷疄鍙寔涔呭寲锛屼笉鏄函鍐呭瓨 demo

闄愬埗锛?
- 鍚屼竴浠芥湰鍦扮洰褰曚竴娆″彧鑳借涓€涓?Qdrant client 瀹炰緥鍗犵敤
- 鏇撮€傚悎鍗曟満寮€鍙戯紝涓嶆槸鏈€缁堢敓浜ч儴缃叉柟寮?
---

## 鏈浠ｇ爜鏀瑰姩鐨勬牳蹇冪偣

### 1. 瀹夎渚濊禆骞跺啓鍥?requirements

鏈鏂板渚濊禆锛?
- `qdrant-client==1.17.1`

杩欐牱鍒汉鎷変綘鐨勯」鐩悗锛屽彧瑕佹寜 `requirements.txt` 瀹夎锛屽氨鑳藉鐜拌繖涓€姝ャ€?
### 2. Qdrant 瀹㈡埛绔敼鎴愮湡瀹炲疄鐜?
`backend/services/qdrant_index_service.py` 鐜板湪涓嶅啀鏄崰浣嶅疄鐜帮紝鑰屾槸鏀寔锛?
- 鏈湴妯″紡鎴栨湇鍔℃ā寮忚嚜鍔ㄥ垏鎹?- collection 鏄惁瀛樺湪妫€鏌?- collection 鍒濆鍖?- payload 缁勮
- point upsert
- 鍚戦噺鏌ヨ
- category / publish_time 杩囨护

### 3. Embedding 鏈嶅姟鏀寔 DashScope 鍏滃簳

`backend/services/embedding_service.py` 鐜板湪鏀寔锛?
- 濡傛灉鏄惧紡閰嶇疆浜?`EMBEDDING_*`锛屼紭鍏堢敤鐙珛 embedding 閰嶇疆
- 濡傛灉娌℃湁鍗曠嫭閰嶇疆锛屼絾 `LLM_BASE_URL` 鏄?DashScope 鍏煎妯″紡鍦板潃锛屽氨鑷姩鍥為€€鍒帮細
  - `https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings`
  - `text-embedding-v4`
  - `LLM_API_KEY`

杩欐牱鍋氱殑濂藉鏄細

- 浣犲綋鍓嶉」鐩凡缁忔湁 DashScope 鐨勬ā鍨嬫帴鍏?- 涓嶉渶瑕佷负浜嗙涓€鐗堝悜閲忔绱㈠啀棰濆鏀瑰緢澶氱幆澧冨彉閲?- 鍏堟妸鏈湴鍚戦噺鍙洖璺戦€?
### 3.1 涓轰粈涔堝缓璁悗闈㈠啀琛ユ樉寮?`EMBEDDING_*`

杩欎竴闃舵涓轰簡鍏堣窇閫氳兘鍔涳紝鍏佽浜?`LLM -> Embedding` 鐨勫洖閫€妯″紡銆?
浣嗕粠宸ョ▼娓呮櫚搴﹀拰闈㈣瘯琛ㄨ揪鏉ヨ锛屽悗缁洿鎺ㄨ崘鏄惧紡鍐欏嚭锛?
```env
EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings
EMBEDDING_API_KEY=浣犵殑_key
EMBEDDING_MODEL=text-embedding-v4
```

杩欐牱鍋氱殑濂藉鏄細

1. 閰嶇疆鑱岃矗鏇存竻妤? 
   鑱婂ぉ妯″瀷鍜?embedding 妯″瀷鏄袱鏉¤兘鍔涳紝涓嶅啀娣峰湪涓€璧枫€?
2. 鍚庣画鍒囨崲 provider 鏇存柟渚? 
   濡傛灉浠ュ悗涓嶇敤 DashScope锛屼篃涓嶉渶瑕佸啀鏀?LLM 鐩稿叧閰嶇疆銆?
3. 闈㈣瘯鏇村ソ瑙ｉ噴  
   鍙互鐩存帴璇达細`LLM` 璐熻矗鐢熸垚锛宍Embedding` 璐熻矗妫€绱紝閰嶇疆鏄嫭绔嬬殑銆?
褰撳墠绯荤粺閲岋紝杩愯鏃剁姸鎬佷篃浼氭槑纭尯鍒嗭細

- `explicit`
- `llm-fallback`
- `partial`
- `missing`

杩欐牱浣犲湪 AI 椤甸噷鑳界洿鎺ョ湅鍒板綋鍓?embedding 鍒板簳鏄樉寮忛厤缃紝杩樻槸娌跨敤鑱婂ぉ妯″瀷閰嶇疆鍥為€€鍑烘潵鐨勩€?
### 4. 鍚戦噺妫€绱粠 placeholder 鍙樻垚鐪熷疄鍙洖

`backend/services/vector_news_retriever.py` 鐜板湪浼氱湡姝ｆ墽琛岋細

1. 鎶婄敤鎴烽棶棰?embedding 鍖?2. 鏍规嵁 category 鍜?timeRange 璁＄畻 filter
3. 鍘?Qdrant 鏌ヨ top-k
4. 鎶婅繑鍥炵偣鏄犲皠鎴?`AiSourceItem`

杩欐剰鍛崇潃锛?
**褰撳墠绯荤粺閲岀殑 `vector-ready` 宸茬粡姝ｅ紡鍗囩骇鎴愪簡 `vector-active`銆?*

### 5. 鏈湴妫€绱㈢姸鎬佸彉鎴愬彲瑙傚療

`news_retrieval_service.py` 鐜板湪浼氭槑纭尯鍒嗭細

- `lexical-baseline`
- `lexical-plus-vector-ready`
- `lexical-plus-qdrant`

杩欐牱浣犲湪 AI 椤靛氨鑳界洿鎺ョ湅鍒板綋鍓嶆湰鍦版绱㈠埌搴曡窇鍦ㄥ摢涓€灞傘€?
### 6. 鍏抽棴搴旂敤鏃朵富鍔ㄩ噴鏀炬湰鍦?Qdrant 鏂囦欢閿?
鍥犱负褰撳墠浣跨敤鐨勬槸鏈湴鎸佷箙鍖栫洰褰曪紝鎵€浠ヨ繖涓€姝ヨ繕琛ヤ簡锛?
- FastAPI 鍏抽棴鏃朵富鍔?`close_client()`

杩欐牱涓嬩竴娆￠噸鍚悗绔椂锛屾洿涓嶅鏄撻亣鍒版湰鍦扮储寮曠洰褰曡鍗犵敤鐨勯棶棰樸€?
---

## 褰撳墠鍚戦噺妫€绱㈤摼璺€庝箞宸ヤ綔

鐜板湪鏈湴鍚戦噺妫€绱㈢殑鐪熷疄娴佺▼鏄細

```text
鏂伴椈姝ｆ枃
-> chunking
-> embedding
-> Qdrant collection upsert

鐢ㄦ埛闂
-> query embedding
-> Qdrant query
-> payload 鏄犲皠涓烘潵婧?-> 鍜?lexical results 铻嶅悎
-> grounded answer
```

鍏朵腑褰撳墠铻嶅悎绛栫暐浠嶇劧淇濇寔淇濆畧锛?
- lexical baseline 缁х画淇濈暀
- vector 浣滀负琛ュ厖鍙洖婧?- 涓嶄細鍥犱负鎺ュ叆鍚戦噺妫€绱㈠氨璁╁師鏈夌ǔ瀹氶摼璺洖閫€

---

## 杩欎竴姝ョ殑楠岃瘉缁撴灉

鏈宸茬粡瀹為檯楠岃瘉杩囷細

1. `qdrant-client` 宸插畨瑁呭埌鍚庣铏氭嫙鐜
2. 鏈湴 Qdrant 鐘舵€佸彲姝ｅ父杩斿洖
3. embedding 鐘舵€佸彲姝ｅ父杩斿洖
4. `preview` 鑳界湅鍒扮湡瀹?chunk
5. `sync` 鐨?`dry-run` 鍙甯歌繑鍥?6. 鐪熷疄绱㈠紩鍚屾鍙妸鏂伴椈 chunk 鍐欏叆 Qdrant
7. 鍐嶇敤鍚屼竴鏉℃柊闂绘爣棰樻彁闂椂锛屽悜閲忓彫鍥炶兘杩斿洖瀵瑰簲鏉ユ簮

涔熷氨鏄锛岃繖涓€姝ヤ笉鏄€滄帴鍙ｉ鐣欌€濓紝鑰屾槸宸茬粡瀹屾垚浜嗙湡瀹炵殑鏈湴鍚戦噺鍙洖闂幆銆?
---

## 鎵嬪姩娴嬭瘯寤鸿

### 1. 鐜鍙橀噺

鍦ㄦ牴鐩綍 `.env` 涓嚦灏戜繚璇侊細

```env
LOCAL_RETRIEVAL_ENGINE=hybrid-ready
ENABLE_VECTOR_RETRIEVAL=true
QDRANT_URL=
QDRANT_LOCAL_PATH=backend/data/qdrant
```

濡傛灉浣犱笉鍗曠嫭閰?embedding锛屼篃鍙互娌跨敤褰撳墠 DashScope锛?
```env
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
LLM_API_KEY=浣犵殑key
EMBEDDING_BASE_URL=
EMBEDDING_API_KEY=
EMBEDDING_MODEL=
```

濡傛灉浣犳兂鎶婇厤缃啓寰楁洿瀹屾暣锛屾帹鑽愮洿鎺ユ敼鎴愶細

```env
LOCAL_RETRIEVAL_ENGINE=hybrid-ready
ENABLE_VECTOR_RETRIEVAL=true

QDRANT_URL=
QDRANT_LOCAL_PATH=backend/data/qdrant
QDRANT_COLLECTION=agentnews_news_chunks
QDRANT_TIMEOUT_SECONDS=5

EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings
EMBEDDING_API_KEY=浣犵殑_key
EMBEDDING_MODEL=text-embedding-v4
```

### 2. 鐪嬬姸鎬?
鍚姩鍚庣鍚庯紝鍏堢湅锛?
- `GET /api/ai/status`
- `GET /api/ai/index/status`

棰勬湡锛?
- `localRetrievalLabel = lexical-plus-qdrant`
- `vectorRetrievalActive = true`
- `indexSyncReady = true`

### 3. 鐪嬪垏鍧?
璋冪敤锛?
- `GET /api/ai/index/preview/1`

棰勬湡锛?
- 鑳界湅鍒版柊闂?1 琚垏鎴愬嚑涓?chunk
- 姣忎釜 chunk 鏈?`snippet / text / charCount`

### 4. 璺戜竴娆?dry-run

璋冪敤锛?
- `POST /api/ai/index/sync`

璇锋眰浣擄細

```json
{
  "dryRun": true,
  "limit": 5
}
```

棰勬湡锛?
- 鐪嬪埌鍑嗗鍚屾澶氬皯鏉℃柊闂汇€佸灏戜釜 chunk
- 涓嶇湡姝ｅ啓鍏?Qdrant

### 5. 鍋氫竴娆＄湡瀹炲悓姝?
浠嶇劧璋冪敤锛?
- `POST /api/ai/index/sync`

璇锋眰浣擄細

```json
{
  "dryRun": false,
  "newsIds": [1]
}
```

棰勬湡锛?
- 杩斿洖 `status = synced`
- 鏈?`upsertedPoints`
- 鏈?`vectorSize`

### 6. 楠岃瘉鍚戦噺鍙洖

鍚屾鍚庯紝鍘?AI 椤甸棶涓€鏉″拰宸插悓姝ユ柊闂荤浉杩戠殑闂銆?
渚嬪锛?
- 鐩存帴鐢ㄨ繖鏉℃柊闂绘爣棰?- 鎴栬€呮崲涓€绉嶆洿璇箟鍖栫殑琛ㄨ揪鏂瑰紡

棰勬湡锛?
- 鏉ユ簮鑳藉懡涓繖鏉℃湰鍦版柊闂?- 褰撳墠鏈湴寮曟搸鐘舵€佹樉绀轰负 `lexical-plus-qdrant`

---

## 杩欎竴闃舵鍦ㄦ柟娉曟紨杩涢噷鐨勬剰涔?
杩欎竴姝ュ緢閫傚悎浣犲悗闈㈠湪闈㈣瘯閲岃В閲婃垚锛?
鈥滄垜娌℃湁鍦ㄤ竴寮€濮嬪氨鎶婄郴缁熷畬鍏ㄥ缓绔嬪湪鍚戦噺妫€绱笂锛岃€屾槸鍏堝仛浜?lexical baseline锛岀‘淇?grounded QA 鍜屾潵婧愮害鏉熷厛鎴愮珛銆傚悗缁啀鎶婃湰鍦版绱㈠眰鎶借薄鍑烘潵锛屾渶鍚庢帴鍏?Qdrant 鍋氱湡瀹炲悜閲忓彫鍥炪€傝繖鏍风郴缁熸槸娌跨潃鍙В閲?baseline -> 鍙彃鎷旂粨鏋?-> 鐪熷疄鍚戦噺妫€绱㈢殑椤哄簭婕旇繘锛岃€屼笉鏄竴涓婃潵鍫嗗緢澶氬熀纭€璁炬柦銆傗€?

杩欐潯婕旇繘璺緞鐨勪环鍊煎湪浜庯細

- 鏂规硶璇曢敊杩囩▼娓呮
- 姣忎竴姝ヤ负浠€涔堝仛閮借寰楅€?- 浠ｇ爜缁撴瀯鍜屽伐绋嬭妭濂忔槸鍖归厤鐨?
---

## 涓嬩竴姝?
`M3.8` 瀹屾垚鍚庯紝涓嬩竴姝ユ洿鑷劧鐨勬柟鍚戞槸锛?
1. 鎶婂綋鍓嶆湰鍦板悜閲忓彫鍥炶繘涓€姝ユ帴鍏ユ洿姝ｅ紡鐨?hybrid retrieval
2. 澧炲姞鏇寸粏鐨?payload filter 鍜?rerank
3. 缁х画鏈?`LangGraph` 椋庢牸宸ヤ綔娴佹帹杩?
涔熷氨鏄锛岃繖涓€姝ュ畬鎴愬悗锛岄」鐩凡缁忎粠鈥滃噯澶囨帴鍚戦噺妫€绱⑩€濊繘鍏ヤ簡鈥滃凡缁忓叿澶囩湡瀹炲悜閲忔绱㈣兘鍔涒€濈殑闃舵銆?
