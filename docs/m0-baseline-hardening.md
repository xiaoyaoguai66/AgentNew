# M0.1 + M0.2 Baseline Hardening

## Goal

This phase hardens the current project before Redis architecture work:

- move runtime configuration out of frontend/backend source code
- remove the frontend LLM API key exposure
- fix core response contracts for news, favorites, and history
- add a backend AI proxy boundary for future Agent work

## What Changed

### 1. Configuration and security

- Added root `.gitignore` to keep `.env`, build output, caches, and logs out of Git.
- Added `.env.example` as the shared configuration template.
- Added local `.env` for current development startup.
- Added `backend/config/settings.py` as the backend settings entrypoint.
- Updated:
  - `backend/config/db_conf.py`
  - `backend/config/cache_conf.py`
  - `backend/main.py`

Key changes:

- MySQL connection now comes from `MYSQL_URL`.
- Redis connection now comes from `REDIS_URL`.
- CORS origins now come from `CORS_ORIGINS`.
- database credentials are no longer hardcoded in Python source
- the frontend no longer stores a real model API key

### 2. News API contract cleanup

- Added:
  - `backend/schemas/news.py`
  - `backend/services/news_service.py`
- Reworked:
  - `backend/schemas/base.py`
  - `backend/crud/news.py`
  - `backend/crud/news_cache.py`
  - `backend/routers/news.py`

Key fixes:

- category cache serialization now uses a dedicated category schema instead of the news schema
- news fields are now normalized to camelCase in API responses
- `/api/news/categories`, `/api/news/list`, `/api/news/detail` now share a clearer response contract
- a service layer was introduced for the news main path

### 3. Favorites and history fixes

- Reworked:
  - `backend/crud/favorite.py`
  - `backend/routers/favorite.py`
  - `backend/crud/history.py`
  - `backend/routers/history.py`

Key fixes:

- favorite list total count now returns a scalar instead of an array
- favorite list join rows now preserve `favoriteTime` and `favoriteId`
- history deletion now truly deletes by `history_id`
- list items now consistently serialize `publishTime`, `favoriteTime`, and `historyId`

### 4. Token and model baseline fixes

- Updated `backend/crud/users.py`
- Updated `backend/models/users.py`

Key fixes:

- token refresh now writes to `expires_at` correctly
- `created_at` and `updated_at` defaults now use callables instead of import-time timestamps

### 5. Backend AI proxy

- Added:
  - `backend/schemas/ai.py`
  - `backend/services/ai_service.py`
  - `backend/routers/ai.py`
- Updated:
  - `frontend/src/config/api.js`
  - `frontend/src/views/AIChat.vue`

Key changes:

- the frontend AI page now calls `/api/ai/chat`
- model key handling is now backend-only
- when `LLM_API_KEY` is missing, the backend returns a safe `503` instead of exposing or guessing secrets

## Runtime Configuration

Use the root `.env` file:

```env
APP_ENV=development
DEBUG=true
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173

MYSQL_URL=mysql+aiomysql://root:your_password@localhost:3306/news_app?charset=utf8mb4
REDIS_URL=redis://localhost:6379/0

LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
LLM_API_KEY=
LLM_MODEL=qwen3-max-preview
```

Notes:

- `MYSQL_URL` is required.
- `LLM_API_KEY` is optional for now.
- if `LLM_API_KEY` is empty, the AI page will show a backend error message instead of sending the secret from the browser.

## How To Run

### Backend

Run from the `backend` directory:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

### Frontend

Run from the `frontend` directory:

```powershell
npm.cmd run dev
```

Optional frontend env:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Verification Done

### Backend

- imported `main.app` successfully using the project virtual environment
- compiled backend source successfully with `python -m compileall`
- verified schema alias output for:
  - `sortOrder`
  - `categoryId`
  - `publishTime`
- verified AI service returns safe `503` when `LLM_API_KEY` is not configured

### Frontend

- `npm.cmd run build` passed after the AI page and API changes

## Why This Matters

This phase makes the project safer and more maintainable:

- secrets are no longer shipped to the browser
- API contracts are now stable enough for frontend refactoring
- the news main path now has a service layer, which is the right place for M1 Redis policies
- favorites and history responses are now reliable enough for later integration testing

## Next Phase

M1 will build on this baseline:

- Redis key design
- TTL strategy
- cache-aside for categories, lists, details, related news
- Redis-based view count aggregation
- hot ranking groundwork
