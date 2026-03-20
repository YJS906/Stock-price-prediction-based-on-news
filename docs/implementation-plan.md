# 한국 주식 뉴스 인텔리전스 MVP 구현 계획

## 1. 저장소 계획

### 제품 목표
- 한국 주식 투자 보조를 위한 실시간 뉴스 중심 웹 플랫폼을 제공한다.
- 최우선 경험은 `실시간 주식 관련 뉴스 피드`이며, 사용자가 페이지를 보고 있는 동안 새 기사가 자동으로 상단에 추가되어야 한다.
- 뉴스에서 테마와 종목으로 자연스럽게 이동하고, 종목 상세에서 차트, 과거 유사 반응, 예측 밴드, 설명 카드를 함께 확인할 수 있어야 한다.
- 예측은 투자 조언이 아니라 확률적 추정으로 제시하며, 근거와 리스크를 함께 표시한다.

### 핵심 원칙
- `mock-first`: 외부 API 없이도 전체 흐름이 동작해야 한다.
- `provider/adapter`: 뉴스, 시세, 번역, 공시 연동은 교체 가능한 인터페이스로 분리한다.
- `real-time first`: 읽기 API에 실시간 갱신 레이어를 붙이고, 클라이언트는 새로고침 없이 자동 반영한다.
- `explainable`: 뉴스-종목 연결, 랭킹, 예측에는 사람이 이해할 수 있는 근거를 남긴다.
- `strong typing`: API 응답, 프론트 타입, 공용 포맷을 공유 패키지로 통합한다.

## 2. 폴더 구조

```text
.
|-- apps
|   |-- api
|   |   |-- app
|   |   |   |-- api
|   |   |   |   `-- routes
|   |   |   |-- core
|   |   |   |-- db
|   |   |   |-- models
|   |   |   |-- repositories
|   |   |   |-- schemas
|   |   |   |-- services
|   |   |   |   |-- pipeline
|   |   |   |   `-- realtime
|   |   |   |-- tasks
|   |   |   `-- tests
|   |   `-- pyproject.toml
|   `-- web
|       |-- app
|       |-- components
|       |   |-- charts
|       |   |-- dashboard
|       |   |-- stocks
|       |   `-- ui
|       |-- lib
|       `-- package.json
|-- packages
|   `-- shared
|       |-- data
|       `-- src
|-- ml
|   |-- scripts
|   |-- src
|   |   `-- newsalpha_ml
|   |       |-- datasets
|   |       |-- evaluation
|   |       |-- features
|   |       |-- models
|   |       `-- pipelines
|   `-- tests
|-- infra
|   |-- docker
|   |-- env
|   `-- scripts
|-- docs
|   |-- implementation-plan.md
|   |-- verification-notes.md
|   `-- windows-docker-troubleshooting.md
|-- README.md
`-- package.json
```

## 3. 스키마 설계

### 핵심 테이블

#### `articles`
- 정규화된 기사 본문 저장
- 주요 컬럼:
  - `id`
  - `provider`
  - `source_type`
  - `source_name`
  - `external_id`
  - `url`
  - `title`
  - `summary`
  - `body`
  - `translated_summary_ko`
  - `published_at`
  - `language`
  - `authors`
  - `image_url`
  - `symbols_hint`
  - `dedupe_hash`
  - `is_stock_relevant`
  - `relevance_score`
  - `sentiment_score`
  - `market_scope`
  - `metadata`
  - `embedding`

#### `article_clusters`
- 유사 기사 묶음과 대표 헤드라인 저장

#### `themes`
- 투자 테마 기준 정보 저장

#### `article_theme_links`
- 다대다 연결
- 기사 하나가 여러 테마에 속할 수 있도록 설계

#### `stocks`
- 국내 상장 종목 마스터

#### `stock_theme_links`
- 종목-테마 연결

#### `stock_news_links`
- 기사-종목 연결과 근거 점수
- `relevance_score`, `upside_score`, `impact_direction`, `reasons` 포함

#### `price_bars`
- 일봉, 주봉, 월봉 등 중장기 차트용 캔들

#### `intraday_price_bars`
- 분봉/장중 차트용 캔들

#### `forecasts`
- 종가 예측 밴드, 방향성 확률, 시간대별 전망 저장

#### `ranking_snapshots`
- 대시보드/테마/이벤트별 종목 랭킹 저장

#### `explanation_cards`
- 연결 근거, 관심 구간, 저항 구간, 리스크 카드 저장

#### `foreign_news_impacts`
- 해외 뉴스 한국어 요약과 국내 시장 영향 해석 저장

### MVP 메모
- 현재 코드베이스는 `market_prices` 단일 테이블에 타임프레임을 분리해 저장한다.
- MVP에서는 이 구조를 유지하되 API 레벨에서 `1m`, `1d`, `1w`, `1mo`를 지원한다.
- `live_feed_sessions`는 서버 상태 없이 클라이언트 기준의 `seen ids`로 충분하므로 이번 단계에서는 별도 테이블 없이 진행한다.

## 4. API 라우트 설계

### 공개 API
- `GET /api/v1/health`
- `GET /api/v1/dashboard`
- `GET /api/v1/articles`
- `GET /api/v1/articles/live`
  - 최신 피드 조회
  - 서버 측 throttled ingest 포함
  - 테마별 필터 지원
- `GET /api/v1/articles/{article_id}`
- `GET /api/v1/themes`
- `GET /api/v1/themes/{theme_slug}`
- `GET /api/v1/stocks`
  - 검색 지원
- `GET /api/v1/stocks/{ticker}`
- `GET /api/v1/stocks/{ticker}/chart?timeframe=1m|1d|1w|1mo`
- `GET /api/v1/stocks/{ticker}/forecast`
- `GET /api/v1/stocks/{ticker}/timeline`
- `GET /api/v1/clusters`
- `GET /api/v1/clusters/{cluster_id}`

### 운영/관리 API
- `GET /api/v1/admin/pipeline-status`
- `POST /api/v1/admin/ingest/run`
- `POST /api/v1/admin/seed/reset`
- `GET /api/v1/admin/evaluations`
- `GET /api/v1/admin/evaluations/{model_name}`

## 5. 실시간 뉴스 갱신 구조 설계

### 선택 방식
- MVP에서는 `짧은 주기 polling`을 사용한다.

### 선택 이유
- 외부 뉴스 provider는 도착 간격이 불규칙하고, SSE/WebSocket보다 polling이 운영 복잡도가 낮다.
- FastAPI 읽기 API 위에 바로 얹을 수 있어 현재 구조를 크게 바꾸지 않는다.
- mock/live provider 모두 같은 API를 통해 갱신할 수 있다.
- 프론트에서 diff, 강조 표시, 정렬 유지 구현이 단순하다.

### 동작 방식
1. 클라이언트가 `/api/v1/articles/live`를 10초 주기로 호출한다.
2. 서버는 내부적으로 마지막 ingest 시각을 확인한다.
3. 기준 시간이 지났으면 provider를 다시 호출해 새 기사만 저장한다.
4. 응답은 최신순 기사 목록과 polling 간격 정보를 반환한다.
5. 프론트는 기존 목록과 비교해 새 기사만 상단에 삽입한다.
6. 새 기사는 `새 뉴스` 시각 효과로 강조하고, 기존에 보던 항목은 일반 스타일로 유지한다.

### mock 실시간 시뮬레이션
- mock provider는 앱 기동 후 시간이 지날수록 더 많은 mock 기사를 노출한다.
- 따라서 외부 API가 없어도 사용자는 페이지 체류 중 새 기사가 들어오는 경험을 확인할 수 있다.

## 6. 모델 모듈 설계

### A. 주식 관련 뉴스 판별
- 규칙 기반 키워드 + 간단한 relevance 점수
- 이후 scikit-learn/LightGBM 분류기로 교체 가능

### B. 테마 분류 모델
- 키워드/시드 taxonomy 기반 multi-label
- 이후 embedding 기반 다중 분류기로 확장 가능

### C. 뉴스-종목 연결/랭킹 모델
- 엔티티/키워드/테마 연결
- 과거 유사 이벤트 반응 점수를 추가 feature로 사용

### D. 단기 예측 모델
- 시세 모멘텀
- 뉴스 relevance
- 랭킹 점수
- 과거 유사 반응 feature를 묶은 baseline
- 결과는 `상승/보합/하락 확률 + 종가 밴드 + 시간대별 전망`

### E. 종목 분석 텍스트 생성
- 뉴스, 테마, 차트 위치, 과거 반응, 예측 밴드를 조합한 설명 카드
- 금지 표현:
  - 수익 보장
  - 단정적 매수 추천

## 7. 구현 우선순위

### 1단계
- 실시간 뉴스 피드 API
- mock 실시간 release
- 프론트 자동 갱신
- 새 뉴스 강조 UI

### 2단계
- 뉴스 카드에 테마/관련 종목 표시
- 대시보드 테마 필터
- 뉴스 페이지 실시간화

### 3단계
- 종목 검색 UX
- 종목 차트 타임프레임 전환
- 종목 상세 설명 카드 보강

### 4단계
- README, 검증 문서, 테스트 보강

## 8. 완료 기준
- 페이지 새로고침 없이 새 뉴스가 자동 반영된다.
- 최신 뉴스가 항상 맨 위에 정렬된다.
- 새 뉴스와 기존 뉴스가 시각적으로 구분된다.
- 테마 클릭/선택으로 같은 테마 뉴스만 볼 수 있다.
- 뉴스 카드에서 관련 종목으로 이동할 수 있다.
- 종목 상세에서 분봉/일봉/주봉/월봉 전환이 가능하다.
- 예측은 밴드와 확률, 근거 카드 형태로 제시된다.
