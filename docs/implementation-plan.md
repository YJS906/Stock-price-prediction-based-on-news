# Korean Stock News Intelligence MVP Implementation Plan

## 1. Repository Plan

### Product scope
- Build a full-stack MVP focused on Korean stock-market decision support driven by filtered and enriched news.
- Support both domestic and foreign news, with Korean-language summaries and Korea-specific market impact interpretation.
- Keep the initial system mock-data first, but preserve clean adapter boundaries for real providers, quote feeds, disclosures, and model serving.

### Architectural principles
- Monorepo with isolated app boundaries and shared domain contracts.
- API-first backend with strongly typed frontend consumers.
- Mock-first services behind provider interfaces so real integrations can replace mocks without rewriting product flows.
- Separate pipeline stages: ingest, normalize, filter, classify, link, rank, forecast, explain.
- Probabilistic outputs only; every prediction view must present uncertainty and rationale.

### Delivery strategy
1. Scaffold repo, workspace tooling, and infrastructure.
2. Implement data schema and FastAPI domain services with mock providers.
3. Expose dashboard-oriented read APIs and ops endpoints.
4. Build polished Next.js UI against the mock-backed API.
5. Add ML baseline scripts, worker placeholders, seed flows, tests, and docs.

## 2. Folder Structure

```text
.
|-- apps
|   |-- api
|   |   |-- app
|   |   |   |-- api
|   |   |   |-- core
|   |   |   |-- db
|   |   |   |-- models
|   |   |   |-- repositories
|   |   |   |-- schemas
|   |   |   |-- services
|   |   |   |-- tasks
|   |   |   `-- tests
|   |   `-- pyproject.toml
|   `-- web
|       |-- app
|       |-- components
|       |-- lib
|       |-- public
|       `-- package.json
|-- packages
|   `-- shared
|       |-- data
|       |-- src
|       `-- package.json
|-- ml
|   |-- src
|   |   `-- newsalpha_ml
|   |       |-- datasets
|   |       |-- features
|   |       |-- models
|   |       |-- pipelines
|   |       `-- evaluation
|   |-- scripts
|   |-- tests
|   `-- pyproject.toml
|-- infra
|   |-- docker
|   |   |-- api.Dockerfile
|   |   |-- web.Dockerfile
|   |   `-- worker.Dockerfile
|   |-- env
|   |   |-- api.env.example
|   |   |-- web.env.example
|   |   `-- postgres.env.example
|   |-- scripts
|   |   |-- dev.ps1
|   |   `-- seed.ps1
|   `-- docker-compose.yml
|-- docs
|   `-- implementation-plan.md
|-- .gitignore
|-- package.json
|-- tsconfig.base.json
`-- README.md
```

## 3. Schema Design

### `articles`
- `id` UUID PK
- `provider` text
- `source_type` enum: `domestic`, `foreign`
- `source_name` text
- `external_id` text nullable
- `url` text unique
- `title` text
- `summary` text
- `body` text nullable
- `translated_summary_ko` text nullable
- `published_at` timestamptz
- `language` text
- `authors` jsonb
- `image_url` text nullable
- `symbols_hint` jsonb
- `dedupe_hash` text indexed
- `is_stock_relevant` boolean
- `relevance_score` numeric(5,4)
- `sentiment_score` numeric(5,4)
- `market_scope` enum: `korea`, `global`, `mixed`
- `metadata` jsonb
- `embedding` vector(384) nullable
- timestamps

### `article_clusters`
- `id` UUID PK
- `cluster_key` text unique
- `headline` text
- `summary` text
- `theme_signal` numeric(5,4)
- `article_count` integer
- `latest_published_at` timestamptz
- `status` enum: `active`, `cooling`, `archived`
- `metadata` jsonb
- timestamps

### `themes`
- `id` UUID PK
- `slug` text unique
- `name_ko` text
- `name_en` text
- `description_ko` text
- `description_en` text nullable
- `market_regime` text
- `is_active` boolean
- `metadata` jsonb
- timestamps

### `stocks`
- `id` UUID PK
- `ticker` text unique
- `name_ko` text
- `name_en` text nullable
- `market` enum: `KOSPI`, `KOSDAQ`, `KONEX`
- `sector` text
- `industry` text
- `description` text
- `country` text default `KR`
- `is_active` boolean
- `metadata` jsonb
- timestamps

### `stock_theme_links`
- `id` UUID PK
- `stock_id` FK
- `theme_id` FK
- `relation_type` text
- `confidence` numeric(5,4)
- `supporting_entities` jsonb
- `metadata` jsonb
- timestamps
- unique `(stock_id, theme_id, relation_type)`

### `stock_news_links`
- `id` UUID PK
- `article_id` FK
- `stock_id` FK
- `cluster_id` FK nullable
- `relevance_score` numeric(5,4)
- `upside_score` numeric(5,4)
- `impact_direction` enum: `positive`, `neutral`, `negative`, `mixed`
- `reasons` jsonb
- `metadata` jsonb
- timestamps
- unique `(article_id, stock_id)`

### `forecasts`
- `id` UUID PK
- `stock_id` FK
- `theme_id` FK nullable
- `cluster_id` FK nullable
- `forecast_horizon` enum: `intraday`, `close`, `t1`
- `direction_up_prob` numeric(5,4)
- `direction_flat_prob` numeric(5,4)
- `direction_down_prob` numeric(5,4)
- `predicted_close_low` numeric(12,2) nullable
- `predicted_close_base` numeric(12,2) nullable
- `predicted_close_high` numeric(12,2) nullable
- `intraday_path` jsonb
- `confidence_interval` jsonb
- `feature_snapshot` jsonb
- `generated_at` timestamptz
- `expires_at` timestamptz

### `ranking_snapshots`
- `id` UUID PK
- `scope_type` enum: `theme`, `cluster`, `dashboard`
- `scope_id` UUID nullable
- `as_of` timestamptz
- `ranking_version` text
- `items` jsonb
- `metadata` jsonb

### `explanation_cards`
- `id` UUID PK
- `stock_id` FK
- `article_id` FK nullable
- `theme_id` FK nullable
- `cluster_id` FK nullable
- `title` text
- `summary_ko` text
- `bullets_ko` jsonb
- `evidence` jsonb
- `risk_flags` jsonb
- `confidence` numeric(5,4)
- `generated_at` timestamptz

### `market_prices`
- `id` UUID PK
- `stock_id` FK
- `price_date` date
- `timeframe` enum: `1m`, `5m`, `1d`
- `open` numeric(12,2)
- `high` numeric(12,2)
- `low` numeric(12,2)
- `close` numeric(12,2)
- `volume` bigint
- `source` text
- `metadata` jsonb
- unique `(stock_id, price_date, timeframe, metadata)`

### `foreign_news_impacts`
- `id` UUID PK
- `article_id` FK unique
- `origin_region` text
- `origin_market` text
- `translated_summary_ko` text
- `korea_market_impact_summary` text
- `affected_themes` jsonb
- `affected_stocks` jsonb
- `impact_confidence` numeric(5,4)
- timestamps

### Supporting association tables
- `article_theme_links`: many-to-many between articles and themes with classifier scores.
- `cluster_article_links`: many-to-many between clusters and articles.

## 4. API Route Design

### Public product routes
- `GET /api/v1/health`
- `GET /api/v1/dashboard`
  - market summary cards, top active themes, latest important news, featured rankings
- `GET /api/v1/themes`
- `GET /api/v1/themes/{theme_slug}`
  - theme details, related clusters, ranked stocks, recent news, confidence labels
- `GET /api/v1/articles`
  - filtered article list with theme tags and relevance scores
- `GET /api/v1/articles/{article_id}`
  - full article context, cluster, linked stocks, foreign impact panel when available
- `GET /api/v1/clusters`
- `GET /api/v1/clusters/{cluster_id}`
- `GET /api/v1/stocks`
  - search and quick cards
- `GET /api/v1/stocks/{ticker}`
  - quote snapshot, chart series, explanation cards, forecast widgets, related timeline
- `GET /api/v1/stocks/{ticker}/timeline`
- `GET /api/v1/stocks/{ticker}/forecast`

### Ops and review routes
- `GET /api/v1/admin/pipeline-status`
- `POST /api/v1/admin/ingest/run`
- `POST /api/v1/admin/seed/reset`
- `GET /api/v1/admin/evaluations`
- `GET /api/v1/admin/evaluations/{model_name}`

## 5. Model Module Design

### A. Stock relevance model
- Input: normalized headline, summary, source metadata.
- Output: `is_stock_relevant`, `relevance_score`, explainable feature summary.
- MVP baseline: TF-IDF + logistic regression.
- Upgrade path: Korean finance-tuned transformer classifier.

### B. Theme classification model
- Input: stock-relevant article text and entity hints.
- Output: multi-label theme probabilities.
- MVP baseline: one-vs-rest linear classifier over TF-IDF features.
- Upgrade path: multilingual transformer with weak supervision taxonomy expansion.

### C. Stock ranking model
- Input: article-theme-stock candidate features, historical event-response features, mention/link strength.
- Output: `relevance_score`, `upside_score`, ranking order.
- MVP baseline: weighted heuristic + gradient boosting placeholder.
- Upgrade path: LightGBM ranking objective or graph-enhanced ranker.

### D. Short-horizon forecast model
- Input: recent price series, ranking signals, theme heat, news velocity, sentiment.
- Output: directional probabilities, close band, intraday segment outlook.
- MVP baseline: calibrated probabilistic heuristic over mock time series.
- Upgrade path: LightGBM quantile models or PyTorch temporal model.

### Shared ML contracts
- `features/` holds feature builders.
- `pipelines/` holds orchestration.
- `evaluation/` holds offline metrics and sample reports.
- `scripts/` expose train/eval/infer entrypoints.

## 6. File Creation Plan

### Repo and tooling
- Root workspace metadata, TypeScript base config, lint/format/test scripts, gitignore.
- Shared package with Korean market domain types, mock fixtures, formatting helpers.

### Backend
- FastAPI app factory, settings, logging, database session, SQLAlchemy models, Pydantic schemas.
- Repositories and services for dashboard, themes, articles, stocks, ops.
- Pipeline components: providers, normalizer, deduper, relevance filter, theme classifier, entity linker, ranker, forecast generator, explanation engine.
- Celery worker bootstrap with mock ingest task.
- Seed and bootstrap logic.
- Unit and integration tests.

### Frontend
- Next.js app router scaffold.
- Shared layout, navigation, dashboard sections, tables/cards, chart components, forecast widgets, skeletons, badges, empty/error states.
- Pages: dashboard, theme, article, stock, ops, evaluations.

### ML
- Mock datasets, feature builders, baseline training/evaluation scripts, model card summaries.

### Infra and docs
- Dockerfiles, compose stack, env templates, helper scripts, README with setup/run/test architecture notes and screenshot placeholders.

## 7. Key Trade-offs

- Use mock-first providers and deterministic synthetic market data to guarantee local end-to-end flows before live integrations.
- Keep PostgreSQL as the single source of truth, even for mock ingestion results, so API and UI reflect the real persistence model.
- Use pgvector fields now but keep embedding generation mocked to avoid forcing external API dependencies in the MVP.
- Share typed contracts in TypeScript for frontend ergonomics; backend remains source-of-truth via OpenAPI and Pydantic schemas.
- Prefer a modular service layer instead of a giant end-to-end ML model so each stage can be independently replaced later.

## 8. Immediate Implementation Order

1. Create monorepo skeleton and workspace configs.
2. Add backend config, schema, seed data, service layer, and API routes.
3. Add frontend UI shell and hook it to backend DTOs.
4. Add ML baseline package and placeholder evaluation artifacts.
5. Add infrastructure files and README, then perform static verification where toolchains are unavailable.
