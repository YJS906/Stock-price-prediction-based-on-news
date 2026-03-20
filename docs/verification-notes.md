# Verification Notes

## Machine setup performed

- Installed Node.js LTS 24.14.0 via `winget`
- Installed Python 3.11.9 via `winget`
- Created repo-local virtualenv at `/.venv`
- Installed backend dependencies from `apps/api`
- Installed frontend dependencies from workspace root
- Installed ML dependencies from `ml`

## Checks completed successfully

### Backend

- `pytest -p no:cacheprovider` in `apps/api`
- Result: `5 passed`

### Frontend

- `npm --workspace apps/web run build`
- `npm --workspace apps/web run lint`
- `npm --workspace apps/web run typecheck`

### ML

- `pytest -p no:cacheprovider` in `ml`
- `python scripts/train_baselines.py`
- Result:
  - `stock-relevance`: accuracy `0.8`
  - `theme-classifier`: subset_accuracy `0.2`
  - `stock-ranking`: r2 `1.0`
  - `short-horizon-forecast`: r2 `0.9851`

### Live HTTP validation

- API:
  - `GET /api/v1/health` -> `200`
  - `GET /api/v1/dashboard` -> `200`
- Web:
  - `GET /` -> `200`
  - `GET /themes` -> `200`
  - `GET /stocks` -> `200`

## Fixes made during runtime validation

- Changed npm workspace package name from invalid `apps/web` to `@newsalpha/web`
- Fixed server-component build strategy to use dynamic/no-store fetching so `next build` does not require the API at build time
- Fixed article-theme persistence order in ingestion pipeline
- Expanded relevance keywords so mock defense/biotech articles are correctly classified as stock-relevant
- Fixed mock embedding dimensionality to match `vector(384)`
- Added Windows Docker preflight and elevated setup helpers with transcript logging
- Added Docker Desktop binary path detection to Windows scripts so `docker` works even when PATH is stale
- Added DB init retries plus Compose healthchecks to remove the Postgres startup race in containers

## Docker validation completed on 2026-03-20

- Installed WSL package `2.6.3`
- Installed Docker Desktop `4.65.0`
- Verified Docker Engine `29.2.1`
- Ran `docker compose -f infra/docker-compose.yml up --build -d`
- Verified `docker compose ps` shows all services running, with healthy `postgres` and `redis`
- Verified `GET /api/v1/health` -> `200`
- Verified `GET /api/v1/dashboard` -> `200`
- Verified `GET /` -> `200`
- Verified `GET /themes` -> `200`
- Verified `GET /stocks` -> `200`

## Post-reboot check on 2026-03-19

- `node -v` -> `v24.14.0`
- `py -V` -> `Python 3.11.9`
- `docker --version` -> command not found
- `wsl --status` -> WSL not installed
- `dism.exe /online /Get-FeatureInfo ...` -> requires elevated permissions in the current shell
- `winget install -e --id Docker.DockerDesktop ...` -> installer reached the administrator handoff step and then failed with exit code `4294967291`

## Added recovery helpers

- `infra/scripts/windows-preflight.ps1`
- `infra/scripts/windows-enable-docker-prereqs.ps1`
- `docs/windows-docker-troubleshooting.md`
- `docs/windows-enable-run.log`
