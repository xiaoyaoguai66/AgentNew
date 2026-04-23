# M4 鑷姩鍖栧啋鐑熸祴璇?
## 1. 杩欎竴杞仛浜嗕粈涔?
杩欎竴杞ˉ鐨勬槸鏈€鍩虹鐨勪竴濂楄嚜鍔ㄥ寲鍐掔儫娴嬭瘯锛岃€屼笉鏄洿閲嶇殑鍗曞厓娴嬭瘯妗嗘灦銆傛牳蹇冩枃浠讹細

- [backend/tests/smoke_api.py](../backend/tests/smoke_api.py)
- [.github/workflows/ci.yml](../.github/workflows/ci.yml)

## 2. 涓轰粈涔堣繖鏍峰仛

褰撳墠椤圭洰宸茬粡鏈夊緢澶氳兘鍔涳細

- 鏂伴椈涓婚摼璺?- AI 鐘舵€佹帴鍙?- 宸ヤ綔娴佸浘瀵煎嚭
- planner baseline eval
- response-level eval

濡傛灉姣忔缁х画杩唬閮藉彧闈犳墜宸ョ偣椤甸潰锛屽緢瀹规槗婕忔帀鏄庢樉鍥炲綊銆? 
浣嗗鏋滀竴寮€濮嬪氨涓婂緢閲嶇殑娴嬭瘯妗嗘灦鍜屽ぇ閲?mock锛屾垚鏈篃涓嶅垝绠椼€?
鎵€浠ヨ繖閲屽厛鍋氱殑鏄細

- compile / build gate
- 鍏抽敭鎺ュ彛 smoke check

## 3. smoke_api.py 鍋氫簡浠€涔?
瀹冧細鐩存帴瀵煎叆 FastAPI app锛屽苟鐢?`TestClient` 璺戣繖浜涘叧閿鏌ワ細

- `/`
- `/health`
- `/api/ai/status`
- `/api/ai/session/start`
- `/api/ai/session/{id}`
- `/api/ai/sessions`
- `/api/ai/workflow/graph`
- `/api/ai/eval/dataset`
- `/api/ai/eval/run`
- `/api/ai/eval/response/dataset`
- `/api/ai/eval/response/run`
- `/api/ai/session/{id}` 鍒犻櫎

杩欓噷浼氭妸鏇村簳灞傜殑鑱婂ぉ鑳藉姏鏇挎崲鎴愪竴涓?fake 鍝嶅簲锛岀洰鐨勪笉鏄祴璇曠湡瀹炴ā鍨嬶紝鑰屾槸楠岃瘉锛?
- 璺敱鏄惁杩樺湪
- schema 鏄惁鍖归厤
- 鍏抽敭涓婚摼璺槸鍚︽病鏂?
## 4. 涓轰粈涔堜笉鍦?CI 閲岀洿鎺ヨ窇鐪熷疄 AI 瀵硅瘽

鍥犱负鐪熷疄 AI 閾捐矾渚濊禆锛?
- LLM key
- Tavily key
- 缃戠粶
- 鏈夋椂杩樹緷璧栨湰鍦版暟鎹簱鍐呭

杩欎細璁?CI 鍙樺緱鑴嗗急锛屼篃浼氳瀹冨け鍘烩€滃熀纭€鍥炲綊闂搁棬鈥濈殑浠峰€笺€?
## 5. 鏈湴鎬庝箞璺?
```powershell
cd backend
.venv\Scripts\python.exe tests\smoke_api.py
```

## 6. 杩欎竴灞傜殑鎰忎箟

杩欎竴杞笉鏄姛鑳藉彉澶氫簡锛岃€屾槸椤圭洰鏇村儚姝ｅ紡宸ョ▼浜嗐€傚洜涓轰粠杩欓噷寮€濮嬶紝椤圭洰涓嶄粎鏈夊姛鑳姐€佹湁鏂囨。锛屼篃鏈夋渶鍩烘湰鐨勮嚜鍔ㄥ寲楠岃瘉鑳藉姏銆?

