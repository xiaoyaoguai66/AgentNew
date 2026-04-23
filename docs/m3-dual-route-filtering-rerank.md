# M3.10 鍙岃矾杩囨护涓庢渶缁堟帓搴忥細鍦?Planner 鍜屽洖绛斾箣闂村啀鍔犱竴灞傛帶鍒?
## 杩欎竴闃舵涓轰粈涔堣鍋?
鍒?`M3.9` 涓烘锛岄」鐩凡缁忓叿澶囷細

- Retrieval Planner
- 鏈湴 lexical baseline
- Qdrant 鏈湴鍚戦噺鍙洖
- 鏈湴 hybrid retrieval
- Tavily Web Search
- 璺ㄦ簮铻嶅悎涓?grounded answer

浣嗕粛鐒惰繕鏈変竴涓伐绋嬮棶棰橈細

**鈥滄嬁鍒颁簡缁撴灉鈥濅笉绛変簬鈥滆繖浜涚粨鏋滈兘閫傚悎鐩存帴杩涘叆鏈€缁堝洖绛斺€濄€?*

鏇村叿浣撳湴璇达紝褰撴椂鐨勭己鍙ｅ寘鎷細

1. `local-first / hybrid / web-first` 铏界劧宸茬粡鍐冲畾浜嗘绱㈣矾寰勶紝浣嗕笉鍚岃矾寰勪笅瀵圭粨鏋滆川閲忕殑瑕佹眰杩樻病鏈夋樉寮忓尯鍒?2. 鏈湴涓?Web 涓よ矾缁撴灉铏界劧浼氳繘鍏ヨ瀺鍚堬紝浣嗗湪铻嶅悎鍓嶇己灏戜竴灞?route-aware 鐨勮繃婊?3. 鏈€缁堟帓搴忚櫧鐒跺凡缁忔湁铻嶅悎閫昏緫锛屼絾杩樻病鏈夋槑纭妸鈥滄湰鍦?hybrid 淇″彿鈥濃€滆法婧愭敮鎸佲€濊繖浜涗俊鎭撼鍏ヨ繍琛屾椂鍙瀵熺姸鎬?
鎵€浠?`M3.10` 鐨勭洰鏍囨槸锛?
**鍦?Retrieval Planner 鍜屾渶缁?grounded answer 涔嬮棿锛屽啀琛ヤ竴灞傚弻璺繃婊や笌鏈€缁堟帓搴忔帶鍒躲€?*

---

## 杩欎竴闃舵鍋氫簡浠€涔?
### 1. 鏂板鍙岃矾杩囨护灞?
鏂板锛?
- `backend/services/dual_route_filter_service.py`

杩欏眰璐熻矗锛?
- 鍦?`local-first / hybrid / web-first` 涓嶅悓璁″垝涓嬶紝瀵规湰鍦板拰 Web 缁撴灉鍒嗗埆鍋?route-aware filtering
- 鎺у埗姣忎竴璺繚鐣欏灏戞潯
- 鎺у埗闃堝€?- 鎺у埗 Web 鍩熷悕閲嶅涓婇檺

杩欐剰鍛崇潃鐜板湪涓嶆槸鈥滄绱㈠畬浜嗗氨鍏ㄦ墧缁欒瀺鍚堝眰鈥濓紝鑰屾槸锛?
```text
Planner
-> Retrieval
-> Route-Aware Filtering
-> Final Rerank / Fusion
-> Grounded Answer
```

### 2. 鏈€缁堟帓搴忔樉寮忓崌绾ф垚 plan-aware cross-source rerank

`retrieval_fusion_service.py` 鐜板湪闄や簡鍘熸湁铻嶅悎閫昏緫锛岃繕鎶婅繖浜涗俊鎭洿鏄庣‘鍦扮撼鍏ヤ簡鏈€缁堟帓搴忥細

- 褰撳墠妫€绱㈣鍒?- 鏈湴鏉ユ簮鏄惁甯?`lexical + vector`
- Web 鏉ユ簮鏄惁鏈夊煙鍚?- 璺ㄦ簮浜掕瘉

鍚屾椂鎶婅繍琛屾椂鐘舵€佹樉寮忓寲鎴愶細

- `finalRerankStrategy = plan-aware-cross-source`

### 3. 鏈湴 hybrid 淇″彿缁х画杩涘叆鏈€缁堟帓搴?
鍦?`M3.9` 閲岋紝涓€鏉℃湰鍦版柊闂诲凡缁忓彲鑳藉甫涓婏細

- `lexical`
- `vector`
- `lexical + vector`

杩欎竴姝ヨ繘涓€姝ュ埄鐢ㄤ簡杩欎釜淇℃伅锛?
- 濡傛灉涓€鏉℃柊闂绘湰鍦板悓鏃惰 lexical 鍜?vector 鍛戒腑锛屼細鍦ㄦ渶缁堟帓搴忛噷缁х画鍔犲垎

杩欐牱鍋氭槸鍚堢悊鐨勶紝鍥犱负杩欎唬琛ㄥ畠鍚屾椂婊¤冻锛?
- 鍏抽敭璇嶇簿纭尮閰?- 璇箟鐩镐技鍖归厤

### 4. 杩愯鏃剁姸鎬佹洿瀹屾暣

`/api/ai/status` 鐜板湪浼氳繑鍥炴洿澶氳皟璇曚俊鎭細

- `localHybridStrategy`
- `dualRouteFilterStrategy`
- `finalRerankStrategy`
- `embeddingConfigMode`

鍓嶇 AI 椤典篃浼氱洿鎺ユ樉绀猴細

- `鏈湴铻嶅悎`
- `鍙岃矾杩囨护`
- `鏈€缁堟帓搴廯

杩欐牱浣犲悗闈㈡紨绀烘椂锛岃兘鏇存竻妤氳鏄庣郴缁熸瘡涓€灞傚埌搴曞湪鍋氫粈涔堛€?
---

## 鎶€鏈悕璇嶈В閲?
### 1. Route-Aware Filtering

鎰忔€濇槸锛?
**鍚屼竴鎵规绱㈢粨鏋滐紝鍦ㄤ笉鍚屾绱㈣鍒掍笅锛岃繃婊よ鍒欎笉涓€鏍枫€?*

渚嬪锛?
- `local-first`
  - 瀵规湰鍦扮粨鏋滄洿瀹藉
  - 瀵?Web 缁撴灉鏇翠繚瀹?
- `web-first`
  - 瀵?Web 缁撴灉鏇村瀹?  - 瀵规湰鍦扮粨鏋滄洿淇濆畧

- `hybrid`
  - 涓よ竟鐩稿骞宠　

杩欎竴姝ョ殑鏍稿績涓嶆槸鈥滄彁鍗囧彫鍥炩€濓紝鑰屾槸鈥滆杩涘叆鏈€缁堝洖绛旂殑璇佹嵁鏇寸鍚堝綋鍓嶈鍒掆€濄€?
### 2. Final Rerank

`rerank` 灏辨槸鈥滄嬁鍒板€欓€夌粨鏋滀箣鍚庯紝鍐嶅仛涓€娆℃帓搴忊€濄€?
杩欓噷鐨?`final rerank` 涓嶆槸鏈湴 lexical/vector 鍐呴儴鐨勮瀺鍚堬紝鑰屾槸锛?
- 鏈湴鍊欓€?- Web 鍊欓€?
鍦ㄦ渶缁堣繘鍏?prompt 涔嬪墠锛岀粺涓€鍐嶆帓涓€娆″簭銆?
### 3. Cross-Source

`cross-source` 鐨勬剰鎬濇槸锛?
鎺掑簭鏃朵笉鍙湅鍗曟潯鏉ユ簮鑷韩锛岃繕鐪嬶細

- 瀹冩槸鍚﹀拰鍏朵粬鏉ユ簮褰㈡垚浜掕瘉
- 鏈湴鍜?Web 鏄惁鍦ㄨ鍚屼竴涓簨浠?
杩欎竴姝ュ鏂伴椈闂瓟鐗瑰埆閲嶈锛屽洜涓烘柊闂诲満鏅噷锛?
- 鍗曟潵婧愬彲鑳戒笉绋冲畾
- 澶氭潵婧愬叡璇嗘洿鍙俊

---

## 涓轰粈涔堣繖涓€闃舵閲嶈

濡傛灉娌℃湁杩欎竴灞傦紝绯荤粺铏界劧宸茬粡鑳藉洖绛旓紝浣嗚繕鏄細鏈変袱涓闄╋細

1. 寮辩浉鍏崇粨鏋滆繘鍏ユ渶缁堝洖绛? 
   瀵艰嚧鍥炵瓟鐪嬭捣鏉モ€滄潵婧愬緢澶氣€濓紝浣嗚瘉鎹泦璐ㄩ噺涓€鑸€?
2. Planner 鍜屾渶缁堢瓟妗堜箣闂寸己灏戠湡姝ｇ殑鎵ц绾︽潫  
   涔熷氨鏄锛岃櫧鐒剁郴缁熻鑷繁鏄?`local-first`锛屼絾鏈€缁堣瘉鎹泦鏈繀鐪熺殑浣撶幇浜嗚繖绉嶅亸濂姐€?
鑰?`M3.10` 鍋氬畬鍚庯紝绯荤粺绗竴娆＄湡姝ｅ叿澶囷細

- 鏄惧紡妫€绱㈣鍒?- route-aware filtering
- final rerank
- grounded answer

杩欏凡缁忛潪甯告帴杩戜竴涓寮忕殑鍙楁帶妫€绱㈠伐浣滄祦浜嗐€?
---

## 褰撳墠杩欎竴姝ョ殑宸ョ▼浠峰€?
杩欎竴姝ュ緢閫傚悎浣犲悗闈㈠湪闈㈣瘯閲岃繖鏍疯锛?
鈥滄垜娌℃湁璁?Planner 鍙仠鐣欏湪鏍囩灞傦紝鑰屾槸缁х画琛ヤ簡涓€灞?route-aware filtering 鍜?final rerank銆傝繖鏍?local-first銆乭ybrid銆亀eb-first 涓嶅彧鏄悕瀛椾笉鍚岋紝鑰屾槸浼氬奖鍝嶆渶缁堝摢浜涜瘉鎹淇濈暀銆佹€庝箞鎺掑簭锛屾渶鍚庡啀杩涘叆 grounded answer銆傗€?

杩欏彞璇濈殑浠峰€煎緢楂橈紝鍥犱负瀹冭鏄庯細

- 浣犱笉鏄彧浼氭惌姒傚康鍥?- 浣犳妸 Planner 鐪熸钀藉埌浜嗘墽琛屽眰
- 浣犵煡閬撴绱㈠伐浣滄祦閲岋紝妫€绱箣鍚庤繕鏈夎繃婊ゅ拰 rerank

---

## 杩欎竴闃舵鎬庝箞娴嬭瘯

### 1. 鐪嬬姸鎬?
璁块棶锛?
- `GET /api/ai/status`

棰勬湡浼氬鍑猴細

- `dualRouteFilterStrategy = route-aware-filtering`
- `finalRerankStrategy = plan-aware-cross-source`

AI 椤甸《閮ㄤ篃搴旂湅鍒帮細

- `鍙岃矾杩囨护 Route-Aware`
- `鏈€缁堟帓搴?Cross-Source`

### 2. 娴嬩笁绫婚棶棰?
#### local-first

闂绀轰緥锛?
- `鏍规嵁鏈湴鏂伴椈搴撴€荤粨涓€涓嬬鎶€鐑偣`

棰勬湡锛?
- 璁″垝鏄?`local-first`
- 鏈湴鏉ユ簮鏇村鏄撲繚鐣欐洿澶氭潯

#### web-first

闂绀轰緥锛?
- `浠婂ぉ鏈€鏂扮殑鍗槦鍙戝皠璁″垝鏈変粈涔堣繘灞昤

棰勬湡锛?
- 璁″垝鏄?`web-first`
- Web 鏉ユ簮鏇村鏄撴帓鍓?
#### hybrid

闂绀轰緥锛?
- `鏈€杩戠鎶€鏂伴椈閲屽摢浜涘彉鍖栨渶鍙兘褰卞搷澶фā鍨嬭涓歚

棰勬湡锛?
- 璁″垝鏄?`hybrid`
- 鏈湴鍜?Web 涓よ竟閮借兘鐣欎笅鏉?
### 3. 鐪嬫湰鍦版潵婧愭爣绛?
鍦ㄦ湰鍦版柊闂绘潵婧愬崱鐗囬噷锛岀户缁湅锛?
- `lexical`
- `vector`
- `lexical+vector`

杩欎竴姝ュ拰 `M3.9` 閰嶅悎璧锋潵锛岃兘甯姪浣犲垽鏂細

- 鏄湰鍦?hybrid 鍦ㄥ伐浣?- 杩樻槸鍙岃矾杩囨护 / 鏈€缁堟帓搴忓湪宸ヤ綔

---

## 鍜屽悗缁?LangGraph 鐨勫叧绯?
`M3.10` 瀹屾垚涔嬪悗锛岀郴缁熺殑鍙楁帶宸ヤ綔娴佹洿鎺ヨ繎锛?
```text
Planner
-> Local Retrieval / Web Search
-> Route-Aware Filtering
-> Final Rerank
-> Grounded Generation
```

杩欏凡缁忛潪甯告帴杩戝悗缁?`LangGraph` 鑺傜偣鍖栨媶鍒嗙殑鑷劧褰㈡€佷簡銆?
鍚庨潰濡傛灉缁х画鍗囩骇锛?
- `Planner` 鍙互鍙樻垚 LangGraph 鑺傜偣
- `Filtering` 鍙互鍙樻垚鍗曠嫭鑺傜偣
- `Rerank` 鍙互缁х画澧炲己
- `Verifier` 涔熷彲浠ョ户缁ˉ杩涙潵

鎵€浠ヨ繖涓€姝ヤ笉鏄复鏃惰ˉ涓侊紝鑰屾槸鍦ㄧ粰鍚庣画鑺傜偣鍖栧伐浣滄祦鎵撳湴鍩恒€?
