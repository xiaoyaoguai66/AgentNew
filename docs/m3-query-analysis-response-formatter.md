# M3.12 Query Analysis 涓?Response Formatter

## 杩欎竴闃舵涓轰粈涔堣鍋?
鍒?`M3.11` 涓烘锛岄」鐩凡缁忔湁锛?
- Retrieval Planner
- Local / Web Retrieval
- Route-Aware Filtering
- Final Rerank
- Verifier

杩欐潯閾捐矾宸茬粡鑳藉伐浣滐紝浣嗚繕瀛樺湪涓や釜缁撴瀯鎬ч棶棰橈細

1. `Planner` 鍓嶉潰鐨勫垽鏂繕涓嶅鏄惧紡  
   寰堝鍏充簬鈥滆繖涓棶棰樻洿鍋忎簨瀹為棶绛旇繕鏄€荤粨鍒嗘瀽鈥濃€滄椂鏁堟€ц姹傞珮涓嶉珮鈥濃€滆寖鍥存洿鍋忔湰鍦拌繕鏄?Web鈥濈殑鍒ゆ柇锛屽叾瀹炶繕娣峰湪 planner 閲屻€?
2. 鏈€缁堝洖绛旇櫧鐒惰兘杩斿洖锛屼絾鈥滃垎鏋愮粨鏋溾€濆拰鈥滅户缁拷闂缓璁€濊繕娌℃湁琚骇鍝佸寲  
   鐢ㄦ埛鍙兘鐪嬪埌涓€娈靛洖澶嶅拰鏉ユ簮鍗＄墖锛屼笉瀹规槗鐞嗚В绯荤粺涓轰粈涔堣繖涔堟煡銆佷笅涓€杞繕鑳芥€庝箞闂€?
鎵€浠ヨ繖涓€闃舵琛ョ殑鏄袱涓妭鐐癸細

- `Query Analysis`
- `Response Formatter`

鐩爣鏄妸褰撳墠鍙楁帶宸ヤ綔娴佹帹杩涙垚锛?
```text
Query Analysis
-> Retrieval Planner
-> Retrieval
-> Filtering
-> Rerank
-> Generation
-> Verifier
-> Response Formatter
```

---

## 杩欎竴闃舵鍋氫簡浠€涔?
### 1. 鏂板 Query Analysis 鑺傜偣

鏂板锛?
- `backend/services/query_analysis_service.py`

杩欎竴灞備細鍏堝闂鍋氬惎鍙戝紡鍒嗘瀽锛屽綋鍓嶈緭鍑哄寘鎷細

- `intent`
- `freshnessNeed`
- `scopePreference`
- `keywordHints`
- `analysisReason`

褰撳墠鐨勬剰鍥惧寘鎷細

- `fact`
- `summary`
- `timeline`
- `compare`

鏃舵晥鎬у寘鎷細

- `low`
- `medium`
- `high`

鑼冨洿鍋忓ソ鍖呮嫭锛?
- `local`
- `hybrid`
- `web`

涔熷氨鏄锛岀幇鍦ㄥ湪杩涘叆 planner 涔嬪墠锛岀郴缁熷凡缁忓厛寰楀埌浜嗕竴浠界粨鏋勫寲鐨勯棶棰樼敾鍍忋€?
### 2. Retrieval Planner 鏀规垚鍩轰簬 Query Analysis 鍐崇瓥

`retrieval_planner_service.py` 鐜板湪涓嶅啀鍙洴鐫€鍘熷闂瀛楃涓诧紝鑰屾槸浼氬弬鑰?Query Analysis 鐨勭粨鏋滀竴璧峰喅绛栥€?
杩欎竴姝ョ殑鎰忎箟鏄細

- `Planner` 缁х画璐熻矗鈥滃喅瀹氳蛋鍝潯妫€绱㈣矾寰勨€?- `Query Analysis` 璐熻矗鈥滄妸闂鐗瑰緛鏄惧紡鎶藉嚭鏉モ€?
杩欐牱鍚庨潰濡傛灉浣犳帴 `LangGraph`锛屽氨寰堝鏄撴媶鎴愪袱涓嫭绔嬭妭鐐癸紝鑰屼笉鏄妸鎵€鏈夐€昏緫閮界硦鍦?planner 閲屻€?
### 3. Query Analysis 杩涘叆 Prompt

`ai_service.py` 鍜?`prompts/news_assistant.py` 鐜板湪浼氭妸 Query Analysis 缁撴灉鍐欒繘鏈€缁?prompt銆?
杩欐剰鍛崇潃妯″瀷鎷垮埌鐨勪笉鍙槸锛?
- 鐢ㄦ埛闂
- 瀵硅瘽鍘嗗彶
- 鏉ユ簮璇佹嵁

杩樺寘鎷細

- 褰撳墠闂鏇村亸浠€涔堟剰鍥?- 鏃舵晥鎬ч渶姹傚己涓嶅己
- 鑼冨洿鍋忓ソ鏇村亸鏈湴杩樻槸 Web
- 鍏抽敭璇嶆彁绀?
杩欎竴姝ョ殑浣滅敤涓嶆槸璁╂ā鍨嬭嚜宸遍噸鏂拌鍒掞紝鑰屾槸璁╂ā鍨嬪湪鈥滃凡缁忚鍒掑ソ鐨勬鏋朵笅鈥濇洿绋冲畾鍦扮粍缁囧洖绛斻€?
### 4. 鏂板 Response Formatter

鏂板锛?
- `backend/services/response_formatter_service.py`

杩欎竴灞傜幇鍦ㄨ礋璐ｄ袱浠朵簨锛?
1. 瑙勮寖鍖栨渶缁堝洖绛旀枃鏈? 
   姣斿鍚堝苟澶氫綑绌鸿銆佷繚璇佽緭鍑烘洿绋冲畾銆?
2. 鐢熸垚杩介棶寤鸿  
   褰撳墠浼氭牴鎹細
   - 妫€绱㈣鍒?   - 璇佹嵁绛夌骇
   - 鍒嗙被
   - 褰撳墠鏉ユ簮

   鑷姩鐢熸垚鏈€澶?3 鏉＄户缁拷闂缓璁€?
渚嬪锛?
- 鈥滃彧鐪嬭繎24灏忔椂锛屽啀閲嶆柊姊崇悊涓€娆¤繖涓棶棰樷€?- 鈥滃彧鍩轰簬鏈湴鏂伴椈搴擄紝閲嶆柊鎬荤粨涓€娆♀€?- 鈥滄妸杩欎欢浜嬪澶фā鍨嬭涓氱殑褰卞搷鍗曠嫭灞曞紑璇翠竴涓嬧€?
### 5. 鍓嶇鎶?Query Analysis 鍜?Follow-Ups 灞曠ず鍑烘潵

AI 椤电幇鍦ㄦ柊澧炰簡涓ょ被灞曠ず锛?
1. 椤堕儴鐘舵€?   - `Analysis Heuristic`
   - `Formatter Follow-Ups`

2. 姣忔潯鍥炵瓟鍐呴儴
   - 闂鍒嗘瀽缁撴灉
   - 缁х画杩介棶寤鸿鎸夐挳

鐢ㄦ埛鐜板湪鍙互鐩存帴鐐瑰嚮杩介棶寤鸿锛屽彂璧蜂笅涓€杞璇濄€?
---

## 鎶€鏈悕璇嶈В閲?
### 1. Query Analysis

`Query Analysis` 鎸囩殑鏄細

**鍦ㄧ湡姝ｅ仛妫€绱箣鍓嶏紝鍏堝鐢ㄦ埛闂鍋氱粨鏋勫寲鐞嗚В銆?*

瀹冨拰 planner 鐨勫尯鍒槸锛?
- Query Analysis锛氭娊鍙栭棶棰樼壒寰?- Planner锛氭牴鎹繖浜涚壒寰佸喅瀹氭绱㈣矾绾?
### 2. Intent

杩欓噷鐨?`Intent` 涓嶆槸澶嶆潅鐨勬剰鍥惧垎绫绘ā鍨嬶紝鑰屾槸涓€涓伐绋嬪寲浠诲姟绫诲瀷鏍囩銆?
褰撳墠鍒嗘垚锛?
- `fact`锛氫簨瀹為棶绛?- `summary`锛氭€荤粨姒傝
- `timeline`锛氫簨浠舵⒊鐞?- `compare`锛氬姣斿垎鏋?
杩欒兘甯姪绯荤粺鍚庨潰鏇寸ǔ瀹氬湴锛?
- 鍐冲畾鍥炵瓟缁撴瀯
- 瑙ｉ噴涓轰粈涔堣蛋鏌愮妫€绱㈣矾寰?
### 3. Freshness Need

`Freshness Need` 鎸囩殑鏄細

**杩欎釜闂瀵光€滄渶鏂颁俊鎭€濈殑渚濊禆绋嬪害銆?*

渚嬪锛?
- 鈥滀粖澶╂渶鏂扮殑鍗槦鍙戝皠璁″垝鈥?-> `high`
- 鈥滄渶杩戜竴鍛ㄧ鎶€鍔ㄦ€佹€荤粨鈥?-> `medium`
- 鈥滅珯鍐呰繖绡囨柊闂昏浜嗕粈涔堚€?-> `low`

### 4. Response Formatter

`Response Formatter` 涓嶆槸绠€鍗曠殑鈥滅編鍖栨枃鏈€濓紝鑰屾槸锛?
**鍦ㄥ洖绛斿凡缁忕敓鎴愬苟鏍￠獙瀹屾垚鍚庯紝鍐嶆妸缁撴灉鏁寸悊鎴愭洿绋冲畾銆佹洿浜у搧鍖栫殑杈撳嚭銆?*

褰撳墠瀹冨仛鐨勬槸锛?
- 鏂囨湰瑙勬暣
- 杩介棶寤鸿鐢熸垚

鍚庨潰杩樺彲浠ョ户缁墿灞曟垚锛?
- 鍥哄畾杈撳嚭娈佃惤
- 寮曠敤鍖鸿鑼冨寲
- follow-up 绛栫暐澧炲己

---

## 涓轰粈涔堣繖涓€姝ラ噸瑕?
杩欎竴闃舵鐨勪环鍊煎湪浜庯紝瀹冭绯荤粺寮€濮嬪叿澶団€滆妭鐐瑰寲宸ヤ綔娴佲€濈殑褰㈡€併€?
涔嬪墠浣犲彲浠ヨ锛?
```text
Planner -> Retrieval -> Answer
```

鐜板湪浣犲彲浠ユ洿瀹屾暣鍦拌锛?
```text
Query Analysis
-> Planner
-> Retrieval
-> Filter
-> Rerank
-> Generator
-> Verifier
-> Formatter
```

杩欏闈㈣瘯浠峰€煎緢楂橈紝鍥犱负瀹冭鏄庯細

- 浣犱笉鏄彧浼氭帴涓€涓亰澶╂帴鍙?- 浣犲湪閫愭鎶婄郴缁熸媶鎴愬彲瑙ｉ噴銆佸彲鏇挎崲鐨勮妭鐐?- 浣犵煡閬撳摢涓€灞傝礋璐ｇ悊瑙ｉ棶棰橈紝鍝竴灞傝礋璐ｅ喅绛栵紝鍝竴灞傝礋璐ｇ粨鏋滆川閲忔帶鍒?
---

## 鎬庝箞娴嬭瘯

### 1. 鐪嬬姸鎬佹帴鍙?
璁块棶锛?
- `GET /api/ai/status`

棰勬湡鏂板瀛楁锛?
- `queryAnalysisEnabled = true`
- `queryAnalysisStrategy = heuristic-query-analysis`
- `responseFormatterEnabled = true`
- `responseFormatterStrategy = evidence-aware-followups`

AI 椤甸《閮ㄥ簲鐪嬪埌锛?
- `Analysis Heuristic`
- `Formatter Follow-Ups`

### 2. 鐪嬪洖绛斿唴鐨勯棶棰樺垎鏋?
闂?3 绫婚棶棰橈細

1. `鏍规嵁鏈湴鏂伴椈搴撴€荤粨涓€涓嬬鎶€鐑偣`
2. `浠婂ぉ鏈€鏂扮殑鍗槦鍙戝皠璁″垝鏈変粈涔堣繘灞昤
3. `鏈€杩戠鎶€鏂伴椈閲屽摢浜涘彉鍖栨渶鍙兘褰卞搷澶фā鍨嬭涓歚

棰勬湡姣忔潯鍥炵瓟閮借兘鐪嬪埌锛?
- 鎰忓浘
- 鏃舵晥
- 鑼冨洿
- 鍒嗘瀽璇存槑

骞朵笖瀹冧滑搴旇鍜岄棶棰樻湰韬殑鐗瑰緛涓€鑷淬€?
### 3. 鐪嬭拷闂缓璁?
姣忔潯鍥炵瓟涓嬫柟搴斿嚭鐜版渶澶?3 鏉¤拷闂缓璁寜閽€?
娴嬭瘯鏂瑰紡锛?
- 鐐瑰嚮浠绘剰寤鸿
- 搴旇兘鐩存帴鍙戣捣鏂颁竴杞彁闂?
### 4. 楠岃瘉涓嶅悓鍦烘櫙鐨勫缓璁槸鍚﹀彉鍖?
渚嬪锛?
- 鎶€鏈被闂鏇村鏄撳嚭鐜扳€滃ぇ妯″瀷琛屼笟褰卞搷鈥?- 寮辫瘉鎹棶棰樻洿瀹规槗鍑虹幇鈥滃彧鐪嬭繎24灏忔椂鈥濃€滃彧鍩轰簬鏈湴鏂伴椈搴撯€?
杩欒鏄?formatter 涓嶅彧鏄浐瀹氬啓姝荤殑妯℃澘锛岃€屾槸浼氭牴鎹綋鍓嶈瘉鎹姸鎬佸彉鍖栥€?
---

## 鍜屽悗缁?LangGraph 鐨勫叧绯?
杩欎竴姝ヨ櫧鐒惰繕娌℃湁姝ｅ紡寮曞叆 LangGraph锛屼絾宸茬粡鍦ㄧ粨鏋勪笂鎻愬墠瀵归綈浜嗭細

- `Query Analysis` 寰堥€傚悎鍙樻垚涓€涓嫭绔嬭妭鐐?- `Response Formatter` 涔熷緢閫傚悎鍙樻垚鏈€缁堣緭鍑鸿妭鐐?
鍥犳鍚庨潰濡傛灉浣犺鎶婃暣鏉￠摼璺縼鎴?LangGraph锛屼富瑕佸仛鐨勬槸锛?
- 鎶婅繖浜涘凡鏈夋湇鍔¤妭鐐瑰寲
- 鐢ㄥ浘缂栨帓杩炴帴璧锋潵

鑰屼笉鏄粠闆堕噸鍐欐暣涓?Agent銆?
