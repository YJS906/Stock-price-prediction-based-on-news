# NewsAlpha

한국 주식 투자 보조를 위한 실시간 뉴스·테마·종목·차트·예측 웹 플랫폼 MVP입니다.

이 저장소는 `mock-first` 방식으로 구성되어 있습니다. 실뉴스 API 키가 없어도 로컬에서 전체 흐름을 바로 확인할 수 있고, 이후 뉴스 provider와 시세 adapter만 교체하면 실제 데이터로 확장할 수 있습니다.

## 핵심 가치

- 실시간 주식 관련 뉴스 피드가 가장 앞에 온다.
- 접속 중 새 뉴스가 자동 반영된다.
- 뉴스별 테마와 관련 종목을 함께 보여준다.
- 종목 상세에서 다중 타임프레임 차트와 확률형 예측 밴드를 제공한다.
- 예측은 투자 조언이 아니라 설명 가능한 확률 추정치로 표현한다.

## 현재 MVP 범위

- 한국/해외 mock 뉴스 수집
- 주식 관련성 필터
- 테마 분류
- 뉴스-종목 연결
- 대시보드 실시간 뉴스 스트림
- 테마별 뉴스 필터
- 종목 검색
- 종목 상세 차트 `1m / 1d / 1w / 1mo`
- 종가 예측 밴드와 단기 방향성 위젯
- 운영 상태 페이지
- 모델 평가 페이지

## 실시간 뉴스 갱신 방식

실시간 반영은 WebSocket 대신 짧은 주기 polling으로 구현했습니다.

- 프론트엔드는 `10초` 간격으로 `GET /api/v1/articles/live` 를 호출합니다.
- 백엔드는 live feed 요청 시 ingest를 `15초` 단위로 제한해 과도한 재수집을 막습니다.
- mock 모드에서는 `seed/reset` 직후 기사 6건으로 시작하고, `20초`마다 국내/해외 기사 1건씩 추가되어 사용자가 페이지를 새로고침하지 않아도 새 뉴스가 위로 올라옵니다.

선택 이유:

- MVP 단계에서 운영 복잡도가 가장 낮습니다.
- 브라우저/프록시 환경 제약이 적습니다.
- 이후 SSE나 WebSocket으로 교체해도 API 경계를 크게 바꾸지 않아도 됩니다.

## 기술 스택

- Frontend: Next.js 14, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy
- Data: PostgreSQL, Redis, pgvector
- ML: pandas, polars, scikit-learn, LightGBM, PyTorch
- Monorepo: `apps/`, `packages/`, `ml/`, `infra/`

## 폴더 구조

```text
apps/
  api/      FastAPI 백엔드, 스키마, 저장소, 파이프라인, 테스트
  web/      Next.js 앱, 대시보드/뉴스/테마/종목 페이지
packages/
  shared/   공용 타입, 포맷터, mock seed 데이터
ml/         베이스라인 모델, 피처 빌더, 평가 코드
infra/      선택적 Docker 설정과 실행 스크립트
docs/       구현 계획, 검증 노트, 스크린샷
```

상세 설계 문서:

- [docs/implementation-plan.md](docs/implementation-plan.md)
- [docs/verification-notes.md](docs/verification-notes.md)

## 주요 페이지

- `/` 대시보드
- `/articles` 실시간 뉴스 피드
- `/themes` 테마 목록
- `/themes/[slug]` 테마 상세
- `/articles/[id]` 뉴스 상세
- `/stocks` 종목 검색
- `/stocks/[ticker]` 종목 상세
- `/admin/ops` 운영 상태
- `/admin/evals` 모델 평가

## 주요 API

- `GET /api/v1/health`
- `GET /api/v1/dashboard`
- `GET /api/v1/articles`
- `GET /api/v1/articles/live`
- `GET /api/v1/articles/{article_id}`
- `GET /api/v1/themes`
- `GET /api/v1/themes/{theme_slug}`
- `GET /api/v1/stocks`
- `GET /api/v1/stocks/{ticker}`
- `GET /api/v1/stocks/{ticker}/chart`
- `GET /api/v1/stocks/{ticker}/forecast`
- `GET /api/v1/stocks/{ticker}/timeline`
- `GET /api/v1/admin/pipeline-status`
- `POST /api/v1/admin/ingest/run`
- `POST /api/v1/admin/seed/reset`

## 데이터 모델

현재 구현 기준 핵심 엔티티:

- `articles`
- `article_clusters`
- `themes`
- `article_theme_links`
- `stocks`
- `stock_theme_links`
- `stock_news_links`
- `market_prices`
- `forecasts`
- `ranking_snapshots`
- `explanation_cards`
- `foreign_news_impacts`

## 로컬 실행

### 1. Python 가상환경과 의존성 설치

```powershell
.\.venv\Scripts\python.exe -m pip install -e .\apps\api[dev]
.\.venv\Scripts\python.exe -m pip install -e .\ml[dev]
```

루트에서 프론트 의존성 설치:

```powershell
npm install
```

`npm` 이 PATH에 없으면 Visual Studio 번들 Node를 사용해도 됩니다.

```powershell
$env:Path='C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Microsoft\VisualStudio\NodeJs;'+$env:Path
npm.cmd install
```

### 2. 로컬 API 환경 변수

API 로컬 실행은 [`apps/api/.env`](apps/api/.env) 를 기준으로 합니다.

기본값:

```env
DATABASE_URL=sqlite+pysqlite:///./newsalpha.db
REDIS_URL=redis://localhost:6379/0
ENABLE_MOCK_SEED_ON_STARTUP=true
LOG_LEVEL=INFO
NEWS_PROVIDER_MODE=mock
MARKET_DATA_PROVIDER_MODE=mock
```

### 3. API 실행

```powershell
cd .\apps\api
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

위 경로가 불편하면 루트에서 아래처럼 실행해도 됩니다.

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir .\apps\api --host 127.0.0.1 --port 8000
```

### 4. 웹 실행

```powershell
$env:API_BASE_URL='http://127.0.0.1:8000'
$env:NEXT_PUBLIC_API_BASE_URL='http://127.0.0.1:8000'
npm --workspace apps/web run dev
```

`npm` 이 PATH에 없으면:

```powershell
$env:Path='C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Microsoft\VisualStudio\NodeJs;'+$env:Path
$env:API_BASE_URL='http://127.0.0.1:8000'
$env:NEXT_PUBLIC_API_BASE_URL='http://127.0.0.1:8000'
npm.cmd --workspace apps/web run dev
```

### 5. 접속 주소

- Web: [http://localhost:3000](http://localhost:3000)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- API Health: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

## 운영 액션

mock 뉴스 추가 ingest:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/admin/ingest/run
```

mock 피드를 처음 상태로 리셋:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/admin/seed/reset
```

## 테스트

API:

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider .\apps\api
```

ML:

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider .\ml
```

Web:

```powershell
npm --workspace apps/web run typecheck
npm --workspace apps/web run lint
npm --workspace apps/web run build
```

## 실제 데이터 교체 포인트

- 뉴스 provider: `apps/api/app/services/pipeline/providers/`
- 시세 adapter: `apps/api/app/services/market_data.py`
- 예측/피처 로직: `apps/api/app/services/pipeline/forecaster.py`
- 공용 mock 데이터: `packages/shared/data/mock-seed.json`

## 주의 사항

- 이 저장소는 현재 mock 중심 MVP입니다. 실거래용 판단 근거로 사용하면 안 됩니다.
- 예측 수치는 확률적 추정치이며, 수익 보장이나 확정적 투자 조언이 아닙니다.
- Docker 설정은 선택 사항이며, 로컬 개발 서버만으로도 전체 흐름을 확인할 수 있습니다.
