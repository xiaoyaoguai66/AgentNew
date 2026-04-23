# AgentNews 婕旂ず鑴氭湰

杩欎唤鑴氭湰鐢ㄤ簬 5 鍒?8 鍒嗛挓椤圭洰婕旂ず銆傜洰鏍囦笉鏄妸鎵€鏈夊姛鑳介兘鐐逛竴閬嶏紝鑰屾槸璁╅潰璇曞畼蹇€熺悊瑙ｏ細杩欐槸涓€涓柊闂诲钩鍙帮紝涔熸槸涓€涓叿澶囨绱€佸伐浣滄祦銆佽娴嬪拰璇勬祴鑳藉姏鐨勬柊闂?Agent銆?
## 1. 寮€鍦哄畾浣?
涓€鍙ヨ瘽鐗堟湰锛?
`AgentNews` 鏄竴涓Щ鍔ㄧ鏂伴椈骞冲彴锛屾垜鍦ㄨ繖涓」鐩噷鎶婁紶缁熸柊闂讳笟鍔￠摼璺拰鏂伴椈 Agent 缁撳悎璧锋潵锛岄噸鐐硅В鍐充簡缂撳瓨銆佹绱€佹椂鏁堟€с€佸够瑙夋帶鍒跺拰宸ヤ綔娴佸彲瑙傛祴鎬ч棶棰樸€?
## 2. 鍏堟紨绀烘柊闂讳骇鍝佷富閾捐矾

寤鸿椤哄簭锛?
1. 鎵撳紑棣栭〉锛屽睍绀哄垎绫诲垏鎹€佺儹闂ㄥ揩璇汇€佹柊闂绘祦
2. 鐐硅繘璇︽儏椤碉紝灞曠ず姝ｆ枃闃呰銆侀槄璇婚噺銆佺浉鍏虫帹鑽?3. 杩涘叆鈥滄垜鐨?/ 鏀惰棌 / 鍘嗗彶鈥濓紝璇存槑鍓嶇宸茬粡浜у搧鍖栵紝涓嶆槸鍙仛浜嗕竴涓?AI 椤甸潰

杩欎竴娈电殑鐩殑锛?
- 璇佹槑椤圭洰涓嶆槸鈥滃彧鏈夎亰澶╂鈥?- 璇佹槑鏈夌湡瀹炰笟鍔″満鏅拰鐢ㄦ埛琛屼负閾捐矾

## 3. 鍐嶆紨绀?AI 鍔╂墜

寤鸿鍑嗗 3 绫婚棶棰橈細

1. `鏍规嵁鏈湴鏂伴椈搴撴€荤粨涓€涓嬬鎶€鐑偣`
   棰勬湡锛歚local-first`

2. `浠婂ぉ鏈€鏂扮殑鍗槦鍙戝皠璁″垝鏈変粈涔堣繘灞昤
   棰勬湡锛歚web-first`

3. `鏈€杩戠鎶€鏂伴椈閲屽摢浜涘彉鍖栨渶鍙兘褰卞搷澶фā鍨嬭涓歚
   棰勬湡锛歚hybrid`

婕旂ず鏃堕噸鐐圭湅锛?
- `retrievalPlan`
- `plannerReason`
- `sources`
- `verificationStatus`
- `workflow trace`
- `session window`

杩欓噷鍙互椤烘墜鐐瑰紑宸︿笂瑙掆€滀細璇濃€濓紝璇存槑鐜板湪鏀寔鍍忎富娴佽亰澶╀骇鍝佷竴鏍峰垏鎹€佹仮澶嶅拰鍒犻櫎鍘嗗彶浼氳瘽銆?
## 4. 灞曠ず宸ヤ綔娴佸浘鍜?LangSmith

鍏堝睍绀猴細

- `GET /api/ai/workflow/graph`

璇存槑锛?
- 褰撳墠涓婚摼璺凡缁忚縼绉诲埌 `LangGraph StateGraph`
- 鑺傜偣鍖呮嫭锛?  `query-analysis -> retrieval-planner -> retrieval -> route-filter -> final-rerank -> generator -> verifier -> response-formatter`

鍐嶅睍绀猴細

- LangSmith trace

璇存槑锛?
- 椤圭洰淇濈暀浜嗘湰鍦?`workflowTrace`
- 鍚屾椂鎺ュ叆浜?LangSmith 瀹樻柟 tracing
- 鎵€浠ユ棦鑳芥湰鍦拌皟璇曪紝涔熻兘骞冲彴鍖栫湅 trace

## 5. 灞曠ず璇勬祴涓庡弽棣堥棴鐜?
灞曠ず锛?
- `GET /api/ai/eval/dataset`
- `POST /api/ai/eval/run`
- `POST /api/ai/eval/response/run`

璇存槑锛?
- 椤圭洰涓嶅彧杩芥眰鈥滆兘鍥炵瓟鈥?- 杩樺仛浜?planner eval 鍜?response-level eval
- 澶辫触 case 浼氭矇娣€涓嬫潵缁х画璋?heuristic 鍜?guardrail

## 6. 鏈€鍚庝竴娈垫€荤粨

鎺ㄨ崘鏀跺熬锛?
杩欎釜椤圭洰涓嶆槸绠€鍗曟妸澶фā鍨嬫帴鍒板墠绔紝鑰屾槸鍏堟妸鏂伴椈涓氬姟閾捐矾鍋氱ǔ锛屽啀鍥寸粫鏂伴椈鍦烘櫙鎶?Agent 鐨勫叧閿棶棰樿ˉ榻愩€傛暣涓繃绋嬩腑锛屾垜閲嶇偣鍋氫簡涓変欢浜嬶細涓€鏄敤 Redis 鎶婇珮棰戣鍐欓摼璺拰浼氳瘽鐘舵€佸仛绋筹紝浜屾槸鎶婃柊闂绘绱粠 lexical baseline 閫愭鍗囩骇鍒版湰鍦?hybrid retrieval 鍜?web search锛屼笁鏄妸 Agent 鍋氭垚鍙В閲娿€佸彲瑙傛祴銆佸彲璇勬祴鐨勫伐浣滄祦锛岃€屼笉鏄粦鐩掕亰澶┿€?
