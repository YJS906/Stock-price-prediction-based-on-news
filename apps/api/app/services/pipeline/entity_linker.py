from dataclasses import dataclass

from app.models import Stock
from app.services.pipeline.normalizer import NormalizedArticle


@dataclass(slots=True)
class StockCandidate:
    stock: Stock
    relevance_score: float
    reasons: list[str]


class EntityLinker:
    def link(self, article: NormalizedArticle, stocks: list[Stock], theme_slugs: list[str]) -> list[StockCandidate]:
        text = f"{article.title} {article.summary} {article.translated_summary_ko or ''}".lower()
        explicit_tickers = set(article.metadata.get("related_tickers", []))
        candidates: list[StockCandidate] = []

        for stock in stocks:
            aliases = [alias.lower() for alias in stock.extra.get("aliases", [])]
            matched = stock.ticker in explicit_tickers or stock.name_ko.lower() in text or any(alias in text for alias in aliases)
            theme_overlap = any(theme_link.theme.slug in theme_slugs for theme_link in stock.themes)
            if not matched and not theme_overlap:
                continue

            reasons: list[str] = []
            score = 0.32
            if stock.ticker in explicit_tickers:
                score += 0.34
                reasons.append("기사 메타데이터에 직접 연결된 종목")
            if stock.name_ko.lower() in text or any(alias in text for alias in aliases):
                score += 0.18
                reasons.append("본문 키워드와 종목/제품명이 직접 매칭")
            if theme_overlap:
                score += 0.18
                reasons.append("해당 투자 테마의 대표 수혜군으로 사전 매핑")

            candidates.append(StockCandidate(stock=stock, relevance_score=min(score, 0.96), reasons=reasons))

        return sorted(candidates, key=lambda item: item.relevance_score, reverse=True)

