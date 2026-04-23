# M3.19 Response Evaluator And Verifier Casebook

## 鏈鍋氫簡浠€涔?
杩欎竴闃舵琛ヤ簡涓ょ被鏀跺熬浣嗛潪甯搁噸瑕佺殑鑳藉姏锛?
1. `Response-Level Evaluator`
2. `Verifier Casebook`

鍓嶉潰鐨?baseline 鏇村亸鈥滄绱㈠墠閾捐矾璇勬祴鈥濓細

- Query Analysis
- Retrieval Planner
- freshness / scope / intent

杩欎竴闃舵寮€濮嬭ˉ鈥滄渶缁堝洖绛斿悎鍚岃瘎娴嬧€濓紝涔熷氨鏄細

- 鍥炵瓟鏈夋病鏈夊唴瀹?- 鏄惁甯︽潵婧?- 鏄惁甯?workflow trace
- 鏄惁甯?follow-up suggestions
- `verificationStatus` 鏄惁钀藉湪鍏佽鑼冨洿鍐?
## 涓轰粈涔堣鍋?Response-Level Evaluator

濡傛灉鍙湁 planner baseline锛屼綘鑳借瘉鏄庘€滃墠鍗婃宸ヤ綔娴佹瘮杈冪ǔ瀹氣€濓紝浣嗚繕涓嶈兘鍥炵瓟锛?
- 鏈€缁堝洖绛旀槸涓嶆槸缁撴瀯瀹屾暣
- guardrail 鐢熸晥鍚庯紝杩斿洖鍚堝悓鏈夋病鏈夎鐮村潖
- accepted / guarded / refused 杩欎笁绫昏緭鍑哄湪鍓嶇鏄惁杩樿兘绋冲畾娑堣垂

鎵€浠ヨ繖涓€闃舵琛ヤ簡涓€涓洿鍋忓伐绋嬪悎鍚岀殑 evaluator銆?
瀹冧笉瑕佹眰鍥炵瓟鏂囨湰閫愬瓧鍖归厤锛屽洜涓烘柊闂?Agent 鐨勭敓鎴愬洖绛斿ぉ鐒朵細鏈夋诞鍔ㄣ€? 
瀹冮噸鐐规鏌ョ殑鏄細

- `status`
- `sources`
- `followUpSuggestions`
- `workflowTrace`
- `reply`

杩欑被绾︽潫鏇撮€傚悎鏂伴椈 Agent 鐨勪腑鍚庢湡璇勬祴銆?
## 涓轰粈涔堣繕瑕佸啓 Verifier Casebook

`Verifier` 鏄柊闂?Agent 閲屽緢鍏抽敭鐨勪竴灞傦紝浣嗗鏋滃彧鍐欎唬鐮侊紝娌℃湁涓€濂椻€滃吀鍨嬪満鏅鏄庘€濓紝鍚庨潰鑷繁澶嶄範浼氬緢闅俱€?
鎵€浠ヨ繖涓€闃舵鎶?verifier 鐨勫吀鍨?case 鏄庣‘鍖栵紝褰㈡垚涓€涓?casebook锛?
- 浠€涔堝満鏅簲 `accepted`
- 浠€涔堝満鏅簲 `guarded`
- 浠€涔堝満鏅簲 `refused`

杩欎細鐩存帴甯姪浣犲悗闈㈠洖绛旓細

- 涓轰粈涔堣鍋?verifier
- verifier 鍏蜂綋绠′粈涔?- verifier 鍜?retrieval / prompt 鐨勮竟鐣屾槸浠€涔?
## 鎶€鏈惈涔?
### 1. Response-Level Evaluator

瀹冧笉鏄涔?judge锛屼篃涓嶆槸璁╂ā鍨嬪幓缁欐ā鍨嬫墦鍒嗐€? 
瀹冩洿鍍忎竴灞?*鍥炵瓟鍚堝悓妫€鏌ュ櫒**銆?
瀹冮噸鐐硅瘎娴嬶細

- `verificationStatus`
- `sourceCount`
- `followUpCount`
- `workflowTraceCount`
- `reply` 鏄惁闈炵┖

### 2. Allowed Statuses

鍥犱负寰堝鏂伴椈闂鏈潵灏变笉閫傚悎鈥滃彧鑳?accepted鈥濄€? 
姣斿鏌愪簺鏈€鏂板姩鎬侀棶棰橈紝鍗充娇绯荤粺杩斿洖 `guarded`锛屼篃鍙兘鏄纭涓恒€?
鎵€浠?response eval 鐢ㄧ殑鏄細

- `allowedStatuses`

鑰屼笉鏄‖缂栫爜蹇呴』鏌愪竴涓姸鎬併€?
### 3. Verifier Casebook

casebook 涓嶆槸娴嬭瘯妗嗘灦锛岃€屾槸涓€濂椻€滃彲澶嶈堪鐨勫伐绋嬬粡楠屾牱渚嬧€濄€?
瀹冪殑浠峰€煎湪浜庯細

- 渚夸簬澶嶇洏
- 渚夸簬鏂囨。灞曠ず
- 渚夸簬闈㈣瘯璁叉竻妤?guardrail 鎬濊矾

## 鏂板鎺ュ彛

- `GET /api/ai/eval/response/dataset`
- `POST /api/ai/eval/response/run`
- `GET /api/ai/eval/response/runs/recent`
- `GET /api/ai/eval/response/failures/recent`

## 濡備綍娴嬭瘯

### 1. 鐪嬫暟鎹泦

璁块棶锛?
- `GET /api/ai/eval/response/dataset`

### 2. 璺?response eval

璇锋眰锛?
- `POST /api/ai/eval/response/run`

绀轰緥锛?
```json
{
  "limit": 3
}
```

### 3. 鐪嬫渶杩?run

璁块棶锛?
- `GET /api/ai/eval/response/runs/recent`

### 4. 鐪嬫渶杩戝け璐?case

璁块棶锛?
- `GET /api/ai/eval/response/failures/recent`

## 闈㈣瘯鎬庝箞璁?
鎺ㄨ崘琛ㄨ堪锛?
> 鎴戞妸璇勬祴鍒嗘垚涓ゅ眰銆傜涓€灞傛槸 Query Analysis 鍜?Retrieval Planner 鐨勭粨鏋勫寲 baseline锛岀敤鏉ヨ瘎浼颁腑闂撮摼璺紱绗簩灞傛槸 Response-Level Evaluator锛岀敤鏉ユ鏌ユ渶缁堝洖绛斿悎鍚岋紝渚嬪 verificationStatus銆乻ources銆亀orkflowTrace 鍜?follow-up 鏄惁绋冲畾銆傝繖璁╅」鐩笉鍙槸鍦ㄤ腑闂撮摼璺彲瑙ｉ噴锛屼篃鍦ㄦ渶缁堣緭鍑哄眰鍙獙璇併€?
