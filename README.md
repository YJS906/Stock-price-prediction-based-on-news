# (주)와이즈경제연구소

한국 주식 투자 보조를 위한 실시간 뉴스·테마·종목 추천·차트·예측 웹 플랫폼 MVP입니다.  
이번 수정에서는 기존 저장소를 유지한 채 아래 문제를 우선 해결했습니다.

- 실시간 뉴스 전용 페이지 추가: `/live`
- 뉴스 정렬/시간 표시를 KST 기준으로 정리
- 사이트를 켜 둔 동안 새 뉴스가 자동 반영되도록 실시간 피드 개선
- 뉴스 상세의 원본보기 링크/fallback 정리
- 종목 검색 범위를 KRX universe까지 확장
- 종목 상세 가격을 live 시세 우선 구조로 보강
- 추천 종목 수를 10개에서 15개로 확대
- 브랜드명을 `newsalpha`에서 `(주)와이즈경제연구소`로 변경

## 핵심 동작 원칙

- 실시간 뉴스 피드가 서비스의 최우선 기능입니다.
- 기본 정렬은 기사 실제 발행시각 기준 내림차순입니다.
- 응답 시간은 KST 오프셋이 포함된 ISO 문자열로 내려갑니다.
- 실시간 반영은 현재 구조에서 가장 단순하고 안정적인 짧은 주기 polling으로 구현했습니다.
- live 데이터가 있으면 live 기사만 우선 노출하고, mock은 fallback일 때만 보여줍니다.
- mock 데이터와 live 데이터는 UI에서 배지와 상태 문구로 구분됩니다.

## 이번 수정 요약

### 1. 실시간 뉴스 경험 강화

- `/live` 페이지를 새로 추가했습니다.
- 새 뉴스가 들어오면 페이지 새로고침 없이 상단에 삽입됩니다.
- 이미 본 뉴스와 새 뉴스가 시각적으로 구분됩니다.
- 연결이 실패하면 자동 재시도합니다.
- 테마 버튼으로 전체/테마별 실시간 뉴스를 바로 전환할 수 있습니다.

### 2. 뉴스 시간/정렬 정확도 개선

- 백엔드 응답에서 모든 `publishedAt`을 KST 기준 ISO로 직렬화합니다.
- 프론트는 `Asia/Seoul` 타임존 기준으로만 렌더링합니다.
- 라이브 기사 우선 조회를 적용해 mock 기사 때문에 상단 피드가 왜곡되는 문제를 줄였습니다.

### 3. 원본보기 링크 보강

- 네이버 금융 기사 링크는 가능한 경우 `n.news.naver.com` 원문 URL로 바로 연결합니다.
- Google News RSS 기반 해외 기사는 직접 원문 URL 확보가 어려울 때 `Google News 경유` 상태를 명시합니다.
- mock 기사 또는 원문 미제공 기사는 버튼/안내 문구로 구분합니다.

### 4. 종목 검색/가격 개선

- KRX 종목 universe 검색 레이어를 추가했습니다.
- DB에 없는 종목도 티커/종목명으로 검색할 수 있습니다.
- 미추적 종목은 기본 시세와 차트 중심으로 상세 페이지를 제공합니다.
- 종목 상세 가격과 차트는 live market provider 우선으로 내려가며, `live / delayed / mock` 상태를 함께 표시합니다.

## 기술 스택

- Frontend: Next.js 14, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy
- Data: PostgreSQL 대응 구조, Redis 대응 구조, pgvector 대응 모델
- Local default runtime: SQLite
- ML: pandas, polars, scikit-learn, LightGBM, PyTorch
- Monorepo: `apps/`, `packages/`, `ml/`, `infra/`

## 디렉터리 구조

```text
apps/
  api/      FastAPI 백엔드
  web/      Next.js 프론트엔드
packages/
  shared/   공용 타입, 포맷터, mock 데이터
ml/         데이터/피처/평가 코드
infra/      선택적 인프라 설정
docs/       구현 계획, 검증 노트, 변경 요약
```

주요 문서:

- [implementation-plan.md](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/docs/implementation-plan.md)
- [remediation-plan.md](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/docs/remediation-plan.md)
- [verification-notes.md](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/docs/verification-notes.md)

## 주요 페이지

- `/` 추천/테마 중심 대시보드
- `/live` 실시간 뉴스 전용 페이지
- `/articles` 뉴스 아카이브
- `/articles/[id]` 뉴스 상세
- `/themes` 테마 목록
- `/themes/[slug]` 테마 상세
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

## 로컬 실행

### 1. Python 의존성 설치

```powershell
.\.venv\Scripts\python.exe -m pip install -e .\apps\api[dev]
.\.venv\Scripts\python.exe -m pip install -e .\ml[dev]
```

### 2. 프론트 의존성 설치

```powershell
npm install
```

`npm`이 PATH에 없으면 Visual Studio 번들 Node를 사용할 수 있습니다.

```powershell
$env:Path='C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Microsoft\VisualStudio\NodeJs;'+$env:Path
npm.cmd install
```

### 3. 기본 환경파일

루트 `.env`는 로컬 개발 기준으로 맞춰져 있습니다.

```env
DATABASE_URL=sqlite+pysqlite:///./newsalpha.db
REDIS_URL=redis://localhost:6379/0
API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEWS_PROVIDER_MODE=hybrid
MARKET_DATA_PROVIDER_MODE=live
```

API 로컬 전용 값이 필요하면 `apps/api/.env`에서 덮어쓸 수 있습니다.

### 4. API 실행

```powershell
cd .\apps\api
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 5. Web 실행

```powershell
$env:API_BASE_URL='http://127.0.0.1:8000'
$env:NEXT_PUBLIC_API_BASE_URL='http://127.0.0.1:8000'
npm --workspace apps/web run dev
```

`npm`이 PATH에 없으면:

```powershell
$env:Path='C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Microsoft\VisualStudio\NodeJs;'+$env:Path
$env:API_BASE_URL='http://127.0.0.1:8000'
$env:NEXT_PUBLIC_API_BASE_URL='http://127.0.0.1:8000'
npm.cmd --workspace apps/web run dev
```

### 6. 접속 주소

- Web: [http://localhost:3000](http://localhost:3000)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- API Health: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

## 실시간 갱신 방식

현재는 WebSocket/SSE 대신 짧은 주기 polling을 사용합니다.

- 프론트는 `GET /api/v1/articles/live`를 주기적으로 호출합니다.
- 백엔드는 ingest를 짧게 throttle 하여 요청마다 과도한 수집이 발생하지 않게 합니다.
- 연결 실패 시 자동 재시도합니다.

선택 이유:

- 현재 구조에서 가장 안정적입니다.
- 프록시/브라우저 환경 의존성이 낮습니다.
- Next.js 서버 컴포넌트와 연동할 때 운영 복잡도가 낮습니다.
- 이후 SSE/WebSocket으로 바꿔도 API 경계는 유지할 수 있습니다.

## 테스트

API:

```powershell
.\.venv\Scripts\python.exe -m pytest .\apps\api
```

ML:

```powershell
.\.venv\Scripts\python.exe -m pytest .\ml
```

Web:

```powershell
npm --workspace apps/web run typecheck
npm --workspace apps/web run lint
npm --workspace apps/web run build
```

## 주의사항

- live provider가 실패하면 일부 화면은 fallback/mock 상태를 명시합니다.
- 예측 값은 확률 기반 추정치이며 투자 조언이 아닙니다.
- 미추적 종목은 시세/차트 위주로만 제공되며, 뉴스 연결/설명 카드가 비어 있을 수 있습니다.
