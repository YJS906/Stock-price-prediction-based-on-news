# Verification Notes

## Verified On

- Date: 2026-03-20
- Local timezone: Asia/Seoul
- Workspace: `C:\Users\YEO_JINSEUNG\OneDrive\바탕 화면\news`

## Runtime Setup Used

- Python: repo-local virtualenv at `/.venv`
- API env: [`apps/api/.env`](../apps/api/.env)
- API DB: local SQLite demo database
- News mode: `mock`
- Market data mode: `mock`
- Web runtime: Next.js production server on port `3000`
- API runtime: Uvicorn on port `8000`
- Node fallback used in this environment:
  `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Microsoft\VisualStudio\NodeJs\`

## Automated Checks

### API

- Command: `python -m pytest -p no:cacheprovider`
- Working directory: `apps/api`
- Result: `7 passed`

### ML

- Command: `python -m pytest -p no:cacheprovider`
- Working directory: `ml`
- Result: `3 passed`

### Web

- Command: `npm --workspace apps/web run typecheck`
- Result: passed
- Command: `npm --workspace apps/web run lint`
- Result: passed
- Command: `npm --workspace apps/web run build`
- Result: passed

## Live API Validation

- `GET /api/v1/health` -> `200`
- `GET /api/v1/articles/live?limit=10` -> `200`
- `GET /api/v1/articles/live?theme=power-grid-nuclear&limit=10` -> `200`
- `GET /api/v1/stocks/000660/chart?timeframe=1d` -> `200`
- `GET /api/v1/stocks/000660/forecast` -> `200`

### Real-time Feed Check

The core product behavior was revalidated after restarting the API with the latest code.

1. `POST /api/v1/admin/seed/reset`
2. Immediate article count: `6`
3. Waited about `25` seconds
4. Live feed count after polling refresh: `8`

Confirmed behavior:

- reset starts with 3 domestic + 3 foreign articles
- new articles are added without page refresh
- newest articles stay at the top of the feed
- live endpoint returns `pollingIntervalMs = 10000`

## Web Route Smoke Checks

- `GET http://localhost:3000/` -> `200`
- `GET http://localhost:3000/articles` -> `200`
- `GET http://localhost:3000/themes` -> `200`
- `GET http://localhost:3000/stocks/000660` -> `200`

## Implementation Notes Confirmed During Verification

- Live feed uses polling instead of WebSocket for MVP simplicity and lower operational overhead.
- Ingest refresh is throttled on the backend to avoid repeated provider fetches on every client poll.
- Local API config now prefers [`apps/api/.env`](../apps/api/.env) over the root `.env`, which prevents accidental use of the Docker/Postgres connection string during local development.
- Mock market data now provides chart points for `1m`, `1d`, `1w`, and `1mo`.
- Stock detail responses include chart timeframe metadata and the dedicated chart endpoint.

## Fixes Applied In This Verification Pass

- Removed duplicate stale Uvicorn processes and restarted the API with the repo-local Python runtime.
- Revalidated mock release timing so `seed/reset` no longer loads the full article set immediately.
- Updated README to reflect the real local run path, polling-based real-time feed design, and current API surface.
