# 실시간 뉴스/검색/가격 신뢰도 개선 계획

## 1. 현재 문제 요약

사용자 확인 기준 주요 문제는 다음과 같다.

1. 실시간 뉴스 시각이 실제 한국 시간과 맞지 않는다.
2. 종목 추천 중심 홈과 별도로 뉴스 자체를 많이 볼 수 있는 실시간 전용 페이지가 부족하다.
3. 자동 갱신은 일부 구현돼 있지만, 실시간 경험과 연결 상태 표현이 약하다.
4. 종목 검색 범위가 지나치게 좁다.
5. 종목 상세 가격이 mock 기준일 때 실제와 크게 다르다.
6. 뉴스 상세 원문 링크가 mock/example URL 또는 Google News wrapper URL로 남는다.
7. 추천 종목 수가 10개로 제한돼 있다.
8. 브랜드명이 여러 곳에 하드코딩돼 있다.

## 2. 원인 분석

### A. 뉴스 시각/정렬 문제

- 기사 `published_at` 는 ingest 과정에서 UTC naive 로 저장된다.
- 프론트는 timezone 정보가 없는 ISO 문자열을 그대로 `Date` 로 파싱한다.
- 그 결과 실제 `KST 19:54` 기사가 화면에서는 `10:54` 로 보일 수 있다.
- 정렬은 DB 기준으로는 대체로 맞지만, 표시가 틀려 사용자가 오래된 기사처럼 인식한다.

### B. 실시간 뉴스 경험 부족

- 현재 `/articles` 에 polling 기반 피드가 있지만, 홈과 충분히 분리된 “뉴스 전용 화면”으로 설계되지 않았다.
- 최신 뉴스 자체보다 추천 흐름이 더 전면에 보인다.
- 자동 갱신 상태, fallback 여부, 새 뉴스 강조, 많은 기사 연속 확인 경험이 약하다.

### C. mock/live 경계 혼재

- 로컬 기본 실행값이 `mock` 이라 실제 뉴스/시세 대신 mock 데이터가 상단에 남는다.
- 이전 mock 데이터가 DB 에 남아 있으면 live 모드로 바뀌어도 사용자에게 섞여 보일 수 있다.
- mock 상태인지 live 상태인지 UI 에서 명확하지 않다.

### D. 종목 검색 누락

- 종목 마스터가 사실상 seed 12종목이라 검색 누락이 구조적으로 발생한다.
- 검색 로직도 `ticker/name_ko/name_en LIKE` 수준으로 단순하다.
- 별칭, 공백 제거, 한글/영문 혼용, 숫자 코드 입력을 충분히 처리하지 못한다.

### E. 가격 정확도 문제

- 로컬 기본 설정이 `MARKET_DATA_PROVIDER_MODE=mock` 이다.
- mock 가격이 상세/차트/추천에 그대로 노출되므로 실제 시세와 오차가 커진다.
- live 경로도 분봉과 일봉/주봉/월봉을 일관되게 제공하지 못해 차트 정합성이 약하다.

### F. 원문 링크 문제

- mock 기사 URL 이 `example.com` 으로 들어간다.
- Google News RSS 링크는 실제 원문이 아니라 Google wrapper URL 이다.
- 상세 화면에서 링크 상태나 fallback 전략이 없다.

### G. 추천 10개 제한

- ingest, ranking snapshot, dashboard presenter 에 `10개` 제한이 하드코딩돼 있다.

### H. 브랜드 하드코딩

- 레이아웃, 상단 네비게이션, 메타데이터에 브랜드 문자열이 분산돼 있다.

## 3. 수정 전략

### 우선순위 1. 실시간 뉴스 전용 페이지

- `/live` 전용 페이지 추가
- 홈과 분리된 고밀도 뉴스 리스트 구성
- 테마 필터 + 전체 보기 전환
- 새 뉴스 상단 삽입 + 강조
- polling 유지

선택 이유:

- 현재 코드베이스에는 polling 기반 live feed 가 이미 존재한다.
- WebSocket/SSE 로 전환하는 것보다 수정 범위가 작고 안정적이다.
- 서버 부하는 `10초 polling + 15초 ingest throttle` 로 제어할 수 있다.

### 우선순위 2. KST 직렬화와 최신순 검증

- API 날짜 직렬화를 KST offset 포함 ISO 문자열로 통일
- 프론트 포맷터도 `Asia/Seoul` 고정
- article/cluster/price/forecast 관련 시각 전부 동일 원칙 적용

### 우선순위 3. 실시간 갱신 신뢰도

- live endpoint 응답에 source mode / timezone / fallback 상태 포함
- 프론트 polling interval 은 서버 응답값 사용
- 실패 시 backoff 와 재연결 표시 추가

### 우선순위 4. 원문 링크 정상화

- 기사별 `originalUrl`, `resolvedUrl`, `linkStatus`, `linkHost` 제공
- Google News wrapper 는 decode 시도
- mock/example 링크는 비정상으로 표시하고 fallback 안내
- 상세 페이지 버튼은 새 탭 `<a>` 링크로 처리

### 우선순위 5. 종목 검색 확장

- KRX 종목 마스터 adapter 추가
- 검색 시 전체 KRX universe 를 기반으로 보강
- 한글명/코드/공백 제거/별칭 기반 점수화 검색
- 검색 결과 부족 시 master source 에서 upsert

### 우선순위 6. 가격 정확도 개선

- live 가격을 기본값으로 사용
- 분봉 + 일봉 기반으로 현재가/차트 일관성 맞춤
- 주봉/월봉은 일봉 집계로 생성
- mock 사용 시 명확한 배지와 경고 문구 표시

### 우선순위 7. 추천 15개 확대

- pipeline/entity linker, ranking snapshot, dashboard/theme/article presenter 모두 15개로 확대

### 우선순위 8. 브랜드 일원화

- 브랜드 상수를 공용 설정으로 분리
- 헤더/title/meta/OG 문구 교체

## 4. 구현 순서

1. 날짜/KST 직렬화 유틸 추가
2. live/mock/source mode 메타데이터 추가
3. `/live` 페이지와 실시간 뉴스용 UI 구성
4. 기사 원문 링크 resolve/fallback 구현
5. KRX 종목 마스터 검색 adapter 추가
6. live 가격 bundle 구조로 차트/현재가 정합성 개선
7. 추천 15개 확장
8. 브랜드 상수화
9. 문서/README/검증 노트 갱신

## 5. 검증 기준

- 한국 시간 기준 최신 뉴스가 상단에 보인다.
- 페이지를 열어 두면 새 뉴스가 새로고침 없이 상단에 추가된다.
- 실시간 뉴스 전용 페이지에서 많은 뉴스와 테마 필터를 바로 쓸 수 있다.
- 원문보기는 실제 원문 URL 또는 명확한 fallback 로 동작한다.
- `삼성전자`, `005930`, `sk 하이닉스`, `LG에너지솔루션` 등 일반 입력으로 검색된다.
- 상세 가격은 live source 기준으로 갱신되며, mock 일 때는 명확히 표시된다.
- 추천 종목이 15개까지 나온다.
- 브랜드가 `(주)와이즈경제연구소` 로 바뀐다.
