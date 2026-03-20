from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.article import ArticleRepository
from app.schemas.api import ArticleDetailResponseSchema, ForeignImpactSchema, RankingEntrySchema, ThemeCardSchema
from app.services.presenters import cluster_card, news_card, ranking_entry, theme_card


class ArticleService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ArticleRepository(db)

    def list_articles(self):
        return [news_card(article) for article in self.repo.list_articles()]

    def get_article_detail(self, article_id: UUID) -> ArticleDetailResponseSchema | None:
        article = self.repo.get_article(article_id)
        if article is None:
            return None

        stock_map = {link.stock.ticker: link.stock for link in article.stock_links}
        linked = [
            ranking_entry(
                {
                    "ticker": link.stock.ticker,
                    "relevance_score": link.relevance_score,
                    "upside_score": link.upside_score,
                    "confidence": min((link.relevance_score + link.upside_score) / 2, 0.98),
                    "reasons": link.reasons,
                },
                stock_map,
            )
            for link in sorted(article.stock_links, key=lambda item: item.upside_score, reverse=True)
        ]

        foreign = None
        if article.foreign_impact:
            foreign = ForeignImpactSchema(
                translatedSummaryKo=article.foreign_impact.translated_summary_ko,
                koreaImpactSummary=article.foreign_impact.korea_market_impact_summary,
                affectedThemes=article.foreign_impact.affected_themes,
                affectedStocks=article.foreign_impact.affected_stocks,
                confidence=article.foreign_impact.impact_confidence,
            )

        return ArticleDetailResponseSchema(
            id=str(article.id),
            title=article.title,
            sourceName=article.source_name,
            sourceType=article.source_type.value,
            publishedAt=article.published_at.isoformat(),
            language=article.language,
            summary=article.summary,
            body=article.body,
            translatedSummaryKo=article.translated_summary_ko,
            url=article.url,
            themes=[ThemeCardSchema(**theme_card(theme)) for theme in article.themes],
            linkedStocks=[RankingEntrySchema(**item) for item in linked],
            cluster=cluster_card(article.clusters[0]) if article.clusters else None,
            foreignImpact=foreign,
        )

