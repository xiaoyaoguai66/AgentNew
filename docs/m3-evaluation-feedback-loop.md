# M3.18 Evaluation Feedback Loop

## 鏈鍋氫簡浠€涔?
杩欎竴闃舵鎶娾€滆瘎娴嬧€濅粠涓€娆℃€х殑鎺ュ彛璋冪敤锛屾帹杩涙垚浜嗕竴涓彲鎸佺画杩唬鐨勫弽棣堥棴鐜€?
鏂板鑳藉姏锛?
- 璇勬祴 run 鑷姩钀界洏
- 澶辫触 case 鑷姩娌夋穩
- LangSmith evaluation-ready 瀵煎嚭
- 涓€杞熀浜?baseline 鐨?heuristic 璋冧紭

鏂板鎺ュ彛锛?
- `GET /api/ai/eval/runs/recent`
- `GET /api/ai/eval/failures/recent`
- `GET /api/ai/eval/langsmith/status`
- `GET /api/ai/eval/langsmith/export`
- `POST /api/ai/eval/langsmith/sync`

## 涓轰粈涔堣鍋氳繖涓€闃舵

鍓嶄竴闃舵铏界劧宸茬粡鏈変簡 baseline锛屼絾杩樼己涓€涓叧閿偣锛?
> 璇勬祴缁撴灉鏈夋病鏈夎娌夋穩涓嬫潵锛屽苟鍙嶅悜椹卞姩绯荤粺浼樺寲锛?
濡傛灉娌℃湁杩欎竴灞傦紝椤圭洰閲屽嵆浣挎湁锛?
- `trace`
- `graph`
- `eval/run`

涔熶粛鐒跺儚鈥滆窇浜嗕竴娆?demo 璇勬祴鈥濄€?
鎵€浠ヨ繖涓€闃舵琛ョ殑涓嶆槸鏂版ā鍨嬭兘鍔涳紝鑰屾槸涓€涓湡姝ｇ殑宸ョ▼闂幆锛?
```text
run eval
-> save run artifact
-> save failure cases
-> analyze mismatches
-> tune heuristics
-> rerun baseline
```

杩欐瘮鍗曠函灞曠ず accuracy 鏇村儚鐪熷疄椤圭洰杩唬銆?
## 杩欐浼樺寲浜嗕粈涔?
閫氳繃 baseline 缁撴灉锛屾垜鍙戠幇涓や釜鏈€鏄庢樉鐨勯棶棰橈細

1. `杩涘睍` 琚繃搴﹀垽鎴?`timeline`
2. `鏈€杩慲 琚繃搴﹀垽鎴?`high freshness`

鎵€浠ヨ繖娆℃病鏈夌洸鐩户缁姞瑙勫垯锛岃€屾槸鎸夊け璐?case 鍙嶆帹 heuristic锛?
- `timeline` 瑙﹀彂璇嶆敼寰楁洿淇濆畧
- `freshness` 鏀规垚浼樺厛鐪?`timeRange`锛屽啀鐪嬫枃鏈俊鍙?- `planner` 涓嶅啀鍥犱负 `summary` 灏遍粯璁ゆ洿鍋?hybrid

浼樺寲鍚庯紝baseline 浠庯細

- `passedCount = 2/6`

鎻愬崌鍒帮細

- `passedCount = 5/6`
- `plannerAccuracy = 0.8333`
- `intentAccuracy = 1.0`
- `freshnessAccuracy = 1.0`
- `scopeAccuracy = 1.0`

璇存槑杩欎竴姝ュ凡缁忎笉鍙槸鈥滆窇璇勬祴鈥濓紝鑰屾槸瀹屾垚浜嗕竴娆″熀浜庤瘎娴嬪弽棣堢殑璋冧紭銆?
## 鎶€鏈惈涔?
### 1. Eval Artifact

灏辨槸鎶婃瘡娆¤瘎娴嬭繍琛岀殑鎽樿缁撴灉鎸佷箙鍖栦笅鏉ャ€? 
褰撳墠浼氳褰曪細

- `runId`
- `recordedAt`
- `totalCount`
- `passedCount`
- `plannerAccuracy`
- `intentAccuracy`
- `freshnessAccuracy`
- `scopeAccuracy`

### 2. Failure Case

灏辨槸鎶婃瘡娆¤瘎娴嬩腑澶辫触鐨勬牱鏈崟鐙矇娣€涓嬫潵銆? 
褰撳墠浼氳褰曪細

- case 鍩烘湰淇℃伅
- 瀹為檯缁撴灉
- 棰勬湡缁撴灉
- mismatch 鍒楄〃

杩欐牱鍚庨潰浣犲彲浠ョ洿鎺ユ寜澶辫触 case 鍘昏皟 planner / analysis锛岃€屼笉鏄噸鏂颁汉宸ュ洖蹇嗛棶棰樸€?
### 3. LangSmith Evaluation-Ready

杩欎竴灞備笉鏄洿鎺ユ浛浠ｆ湰鍦?baseline锛岃€屾槸鎶婃湰鍦拌瘎娴嬮泦瀵煎嚭鎴愭洿閫傚悎 LangSmith Dataset 鐨勭粨鏋勶細

- `inputs`
- `outputs`
- `metadata`

杩欐牱鍚庨潰浣犲彲浠ワ細

- 缁х画鍦ㄦ湰鍦拌窇 baseline
- 鎴栬€呮妸鏁版嵁闆嗗悓姝ュ埌 LangSmith 骞冲彴鍋氭洿姝ｅ紡鐨勮瘎娴嬪疄楠?
## 鏈瀹炵幇鍘熺悊

### 1. 璇勬祴缁撴灉鑷姩钀界洏

姣忔璋冪敤 `POST /api/ai/eval/run` 鏃讹細

- 鍏堢敓鎴?`runId`
- 鎵ц baseline
- 鎶?run 鎽樿鍐欏叆 `eval_runs.jsonl`
- 鎶婂け璐?case 鍐欏叆 `eval_failures.jsonl`

### 2. LangSmith 瀵煎嚭

LangSmith 瀵煎嚭褰撳墠涓嶇洿鎺ヤ緷璧栨ā鍨嬭緭鍑猴紝鑰屾槸鍏堝鍑猴細

- 闂杈撳叆
- 鏈熸湜鐨?plan / intent / freshness / scope
- case metadata

杩欐槸涓€涓緢閫傚悎涓湡椤圭洰鐨勮瘎娴嬫暟鎹舰鎬侊紝鍥犱负绋冲畾銆佸彲瑙ｉ噴锛屼篃鏂逛究鍚庨潰鎵╁睍銆?
## 濡備綍娴嬭瘯

### 1. 鍏堣窇 baseline

璇锋眰锛?
- `POST /api/ai/eval/run`

绀轰緥锛?
```json
{
  "limit": 6
}
```

### 2. 鏌ョ湅鏈€杩?run

璁块棶锛?
- `GET /api/ai/eval/runs/recent`

### 3. 鏌ョ湅鏈€杩戝け璐?case

璁块棶锛?
- `GET /api/ai/eval/failures/recent`

### 4. 鏌ョ湅 LangSmith evaluation 鐘舵€?
璁块棶锛?
- `GET /api/ai/eval/langsmith/status`

### 5. 瀵煎嚭 LangSmith dataset payload

璁块棶锛?
- `GET /api/ai/eval/langsmith/export`

### 6. 鍚屾鍒?LangSmith

璇锋眰锛?
- `POST /api/ai/eval/langsmith/sync`

濡傛灉褰撳墠 LangSmith 鏈厤缃紝绯荤粺浼氬畨鍏ㄨ繑鍥炩€滀粎鏀寔鏈湴瀵煎嚭鈥濓紱濡傛灉宸查厤缃紝鍒欎細灏濊瘯鍒涘缓 dataset 骞朵笂浼?examples銆?
## 闈㈣瘯鎬庝箞璁?
鎺ㄨ崘琛ㄨ堪锛?
> 鎴戜笉浠呭仛浜?LangGraph 宸ヤ綔娴佸拰 LangSmith tracing锛岃繕琛ヤ簡涓€涓?evaluation feedback loop銆傚叿浣撳仛娉曟槸鍏堟瀯寤虹粨鏋勫寲 baseline锛岃嚜鍔ㄨ褰曟瘡娆¤瘎娴?run 鍜屽け璐?case锛屽啀鏍规嵁 mismatch 鍙嶆帹 Query Analysis 涓?Retrieval Planner 鐨?heuristic 璋冧紭銆傚悗缁繕鎶婅繖缁勮瘎娴嬫暟鎹鍑烘垚 LangSmith-ready dataset锛屾柟渚跨户缁仛骞冲彴鍖栬瘎娴嬪拰瀹為獙銆?
