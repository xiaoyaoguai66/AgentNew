# M4 CI 涓庝氦浠樺眰鍔犲浐

## 1. 杩欎竴杞仛浜嗕粈涔?
杩欎竴杞病鏈夌户缁彔 Agent 鍔熻兘锛岃€屾槸鎶婇」鐩線鈥滃彲浜や粯銆佸彲鍗忎綔銆佸彲鏀惧埌 GitHub鈥濇柟鍚戞帹杩涗簡涓€灞傦細

- 娓呯悊榛樿妯℃澘鏂囦欢鍜岃繍琛屼骇鐗?- 瀹屽杽 `.gitignore` 涓?`.dockerignore`
- 澧炲姞 `README.md`
- 澧炲姞鏋舵瀯鎬昏鍜屾枃妗ｇ储寮?- 澧炲姞 `Dockerfile + docker-compose.yml`
- 澧炲姞鍩虹 GitHub Actions CI
- 澧炲姞 `/health` 鍋ュ悍妫€鏌ユ帴鍙?
## 2. 涓轰粈涔堣繖涓€姝ラ噸瑕?
鍒拌繖涓樁娈碉紝椤圭洰鐨勬牳蹇冭兘鍔涘凡缁忔瘮杈冨畬鏁淬€傚啀缁х画鍙姞鍔熻兘锛屾敹鐩婁細瓒婃潵瓒婂皬锛涗絾濡傛灉娌℃湁浜や粯灞傦紝闈㈣瘯鍜?GitHub 灞曠ず鏃朵細鍑虹幇涓や釜闂锛?
1. 椤圭洰鈥滆兘璁测€濓紝浣嗕笉澶熷儚姝ｅ紡宸ョ▼椤圭洰
2. 浠ｇ爜涓€鏃︾户缁凯浠ｏ紝灏辩己灏戞渶鍩虹鐨勮嚜鍔ㄩ獙璇?
鎵€浠ヨ繖涓€姝ョ殑閲嶇偣涓嶆槸鏂板涓氬姟鑳藉姏锛岃€屾槸鎻愰珮宸ョ▼瀹屾垚搴︺€?
## 3. 鏂板鐨勪氦浠樺眰鍐呭

### Docker 鍖?
鏂板鏂囦欢锛?
- [docker-compose.yml](../docker-compose.yml)
- [backend/Dockerfile](../backend/Dockerfile)
- [frontend/Dockerfile](../frontend/Dockerfile)
- [frontend/nginx.conf](../frontend/nginx.conf)

褰撳墠鏂规鐨勫畾浣嶆槸锛?
- MySQL 鍜?Redis 鐙珛瀹瑰櫒
- Backend 鐙珛瀹瑰櫒
- Frontend 闈欐€佹瀯寤哄悗鐢?Nginx 鎵樼
- Qdrant 褰撳墠浠嶈蛋 backend 鍐呴儴 local persistent mode

杩欐牱鍋氱殑鍘熷洜锛?
- 鐜板湪鏈€閲嶈鐨勬槸鎶婃绱㈡灦鏋勮窇閫氾紝鑰屼笉鏄厛鎶?Qdrant 鏈嶅姟鍖栭儴缃插仛澶嶆潅
- 鏈湴 Qdrant 妯″紡鏇村埄浜庡崟鏈哄紑鍙戝拰婕旂ず
- 鍚庨潰濡傛灉鍒囧埌鐙珛 Qdrant 鏈嶅姟锛屾敼鐨勬槸閮ㄧ讲褰㈡€侊紝涓嶆槸鏁翠綋妫€绱㈡灦鏋?
### 鍋ュ悍妫€鏌?
鏂板鎺ュ彛锛?
- `GET /health`

鎰忎箟锛?
- 璁╅儴缃插悗鑳藉揩閫熷垽鏂湇鍔℃槸鍚﹀惎鍔ㄦ垚鍔?- 涓哄悗缁鍣ㄧ紪鎺掋€丆I smoke check 鍜屽彲瑙傛祴鎬ч鐣欏叆鍙?
### GitHub Actions CI

鏂板鏂囦欢锛?
- [.github/workflows/ci.yml](../.github/workflows/ci.yml)

褰撳墠 CI 鍋氱殑鏄渶鍩虹浣嗘渶鏈変环鍊肩殑鍑犱欢浜嬶細

- 鍚庣渚濊禆瀹夎 + targeted compile + app import
- backend smoke
- backend integration
- frontend build

杩欒繕涓嶆槸瀹屾暣娴嬭瘯浣撶郴锛屼絾宸茬粡鑳芥尅浣忔渶甯歌鐨勫洖褰掞細

- 鍚庣璇硶閿欒
- FastAPI 搴旂敤瀵煎叆閿欒
- 鍓嶇鎵撳寘澶辫触
- 浼氳瘽涓婚摼璺洖褰?
## 4. 浠撳簱娓呯悊

杩欎竴灞傝繕娓呯悊浜嗭細

- 榛樿 Vite 妯℃澘娈嬬暀鏂囦欢
- `.cursor / .idea / __pycache__ / debug log / 鏈湴 qdrant 绱㈠紩 / eval jsonl`

杩欎簺鍐呭鏈湴寮€鍙戝彲鑳戒細閲嶆柊鐢熸垚锛屼絾鐜板湪宸茬粡閫氳繃 ignore 瑙勫垯鏀跺彛锛屼笉浼氱户缁薄鏌撲粨搴撱€?
## 5. 鍜屾暣浣撹鍒掔殑鍏崇郴

杩欎竴灞傚睘浜庢渶鍒濊矾绾垮浘閲岀殑 `M4 宸ョ▼鍖栨敹灏綻銆? 
瀹冧笉鏄€滀富鍔熻兘瀹炵幇鈥濈殑涓€閮ㄥ垎锛岃€屾槸鎶婇」鐩粠鈥滅爺绌跺瀷浣滃搧鈥濆線鈥滀紒涓氬寲浜や粯浣滃搧鈥濇帹杩涚殑鍏抽敭姝ラ銆?
## 6. 闈㈣瘯閲屾€庝箞璁?
鍙互杩欐牱姒傛嫭锛?
鏍稿績鍔熻兘瀹屾垚鍚庯紝鎴戞病鏈夊仠鍦ㄢ€滆兘璺戔€濓紝鑰屾槸缁х画琛ヤ簡浜や粯灞傦紝鍖呮嫭 Docker Compose銆佸仴搴锋鏌ャ€丷EADME銆佹灦鏋勬€昏鍜?GitHub Actions CI銆傝繖鏍烽」鐩湪 GitHub 涓婁笉浠呰兘灞曠ず鍔熻兘锛屼篃鑳戒綋鐜板熀鏈殑宸ョ▼浜や粯鑳藉姏銆?
