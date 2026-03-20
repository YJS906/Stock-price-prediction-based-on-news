# 2026-03-20 변경 요약

## 해결한 문제

1. 실시간 뉴스라고 표시되지만 오래된 시간이 상단에 보이던 문제
- 기사 시간을 KST 오프셋 포함 ISO 문자열로 직렬화하도록 수정
- 프론트 렌더링도 `Asia/Seoul` 기준으로 통일

2. 실시간 뉴스 전용 페이지 부재
- `/live` 페이지 추가
- 뉴스 자체가 중심인 고밀도 리스트 구성

3. 사이트를 켜 둔 동안 새 뉴스 자동 반영 부족
- polling 기반 자동 갱신 강화
- 새 뉴스 강조, 재연결 상태 표시 추가

4. 종목 검색 누락
- KRX universe 검색 서비스 추가
- DB에 없는 종목도 검색 가능

5. 종목 가격 정확도 부족
- 종목 상세/차트에서 live market provider 우선 사용
- `live / delayed / mock` 상태와 가격 안내 문구 추가

6. 뉴스 원본보기 실패
- 네이버 금융 링크는 가능한 경우 직접 원문 URL로 변환
- Google News 경유 링크는 상태를 명시하고 fallback 출처 홈 링크 제공
- mock 기사 링크는 실제 원문처럼 보이지 않도록 처리

7. 추천 종목 수 10개 제한
- 랭킹 snapshot, ingest, 대시보드 노출을 15개로 확대

8. 브랜드명 변경
- `(주)와이즈경제연구소`로 헤더, 메타, 아이콘 반영

## 주요 파일

- [apps/api/app/services/presenters.py](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/apps/api/app/services/presenters.py)
- [apps/api/app/services/stocks.py](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/apps/api/app/services/stocks.py)
- [apps/api/app/services/market_data.py](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/apps/api/app/services/market_data.py)
- [apps/api/app/repositories/article.py](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/apps/api/app/repositories/article.py)
- [apps/web/app/live/page.tsx](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/apps/web/app/live/page.tsx)
- [apps/web/components/dashboard/news-stream.tsx](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/apps/web/components/dashboard/news-stream.tsx)
- [apps/web/app/stocks/[ticker]/page.tsx](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/apps/web/app/stocks/[ticker]/page.tsx)
- [apps/web/app/articles/[id]/page.tsx](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/apps/web/app/articles/[id]/page.tsx)

## 검증 결과

- API 테스트: `7 passed`
- ML 테스트: `3 passed`
- Web: `typecheck`, `lint`, `build` 통과
- 로컬 라이브 ingest: 국내/해외 live provider 기준 `52건` 수집 확인
