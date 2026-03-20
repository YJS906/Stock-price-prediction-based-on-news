from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.enums import SourceType
from app.models import (
    Article,
    ArticleCluster,
    ExplanationCard,
    ForeignNewsImpact,
    RankingSnapshot,
    Stock,
    StockNewsLink,
    Theme,
    article_theme_links,
    cluster_article_links,
)
from app.services.pipeline.deduper import ArticleDeduper
from app.services.pipeline.entity_linker import EntityLinker
from app.services.pipeline.explanation import ExplanationEngine
from app.services.pipeline.forecaster import ForecastEngine
from app.services.pipeline.normalizer import ArticleNormalizer
from app.services.pipeline.providers.base import NewsProvider
from app.services.pipeline.ranker import RankingEngine
from app.services.pipeline.relevance import StockRelevanceClassifier
from app.services.pipeline.theme_classifier import ThemeClassifier


class IngestionPipelineService:
    def __init__(self) -> None:
        self.normalizer = ArticleNormalizer()
        self.deduper = ArticleDeduper()
        self.relevance = StockRelevanceClassifier()
        self.theme_classifier = ThemeClassifier()
        self.entity_linker = EntityLinker()
        self.ranking_engine = RankingEngine()
        self.forecast_engine = ForecastEngine()
        self.explanation_engine = ExplanationEngine()

    def reset_generated_content(self, db: Session) -> None:
        db.execute(delete(ExplanationCard))
        db.execute(delete(ForeignNewsImpact))
        db.execute(delete(StockNewsLink))
        db.execute(delete(RankingSnapshot))
        db.execute(delete(cluster_article_links))
        db.execute(delete(article_theme_links))
        db.execute(delete(Article))
        db.execute(delete(ArticleCluster))

    def run(self, db: Session, providers: list[NewsProvider]) -> dict:
        themes = db.scalars(select(Theme).where(Theme.is_active.is_(True))).all()
        stocks = db.scalars(select(Stock).where(Stock.is_active.is_(True))).all()
        stored = 0
        relevant = 0
        cluster_registry: dict[str, ArticleCluster] = {}
        processed_at = datetime.now(UTC)
        articles_seen = 0
        provider_statuses: list[dict] = []

        for provider in providers:
            try:
                fetched = provider.fetch()
                provider_statuses.append(
                    {
                        "name": provider.name,
                        "kind": provider.source_type.value,
                        "status": "healthy",
                        "articlesSeen": len(fetched),
                    }
                )
            except Exception as exc:
                provider_statuses.append(
                    {
                        "name": provider.name,
                        "kind": provider.source_type.value,
                        "status": f"degraded: {type(exc).__name__}",
                        "articlesSeen": 0,
                    }
                )
                continue

            articles_seen += len(fetched)
            for raw_article in fetched:
                normalized = self.normalizer.normalize(raw_article)
                published_at = self._as_utc_naive(normalized.published_at)
                if self.deduper.is_duplicate(db, normalized):
                    continue

                relevance = self.relevance.evaluate(normalized.title, normalized.summary)
                article = Article(
                    provider=normalized.provider,
                    source_type=normalized.source_type,
                    source_name=normalized.source_name,
                    external_id=normalized.external_id,
                    url=normalized.url,
                    title=normalized.title,
                    summary=normalized.summary,
                    body=normalized.body,
                    translated_summary_ko=normalized.translated_summary_ko,
                    published_at=published_at,
                    language=normalized.language,
                    authors=normalized.authors,
                    image_url=normalized.image_url,
                    symbols_hint=normalized.symbols_hint,
                    dedupe_hash=normalized.dedupe_hash,
                    is_stock_relevant=relevance.is_stock_relevant,
                    relevance_score=relevance.relevance_score,
                    sentiment_score=relevance.sentiment_score,
                    market_scope=normalized.market_scope,
                    extra=normalized.metadata,
                    embedding=[0.0] * 384,
                )

                db.add(article)
                theme_scores = self.theme_classifier.classify(normalized, themes)
                article.themes = [theme for theme in themes if theme.slug in theme_scores]

                cluster_key = normalized.metadata.get("cluster_key") or f"cluster-{normalized.dedupe_hash[:8]}"
                cluster = cluster_registry.get(cluster_key)
                if cluster is None:
                    cluster = db.scalar(select(ArticleCluster).where(ArticleCluster.cluster_key == cluster_key))
                if cluster is None:
                    cluster = ArticleCluster(
                        cluster_key=cluster_key,
                        headline=normalized.metadata.get("cluster_headline") or normalized.title,
                        summary=normalized.summary,
                        theme_signal=max(theme_scores.values()) if theme_scores else 0.4,
                        article_count=0,
                        latest_published_at=published_at,
                        extra={"theme_hints": list(theme_scores.keys())},
                    )
                    db.add(cluster)
                    db.flush()

                cluster.article_count += 1
                cluster.latest_published_at = max(
                    self._as_utc_naive(cluster.latest_published_at),
                    published_at,
                )
                cluster.articles.append(article)
                cluster_registry[cluster_key] = cluster

                db.flush()
                stored += 1

                if relevance.is_stock_relevant:
                    relevant += 1
                    candidates = self.entity_linker.link(normalized, stocks, list(theme_scores.keys()))
                    for candidate in candidates[:15]:
                        theme_boost = 0.05 if any(link.theme.slug in theme_scores for link in candidate.stock.themes) else 0.0
                        upside_score, direction = self.ranking_engine.score_link(
                            relevance.sentiment_score,
                            candidate.relevance_score,
                            article.source_type.value,
                            theme_boost,
                        )

                        db.add(
                            StockNewsLink(
                                article_id=article.id,
                                stock_id=candidate.stock.id,
                                cluster_id=cluster.id,
                                relevance_score=round(candidate.relevance_score, 4),
                                upside_score=upside_score,
                                impact_direction=direction,
                                reasons=candidate.reasons,
                                extra={"provider": provider.name},
                            )
                        )

                        explanation = self.explanation_engine.build_article_summary(
                            candidate.stock.name_ko,
                            article,
                            article.themes,
                            candidate.reasons,
                        )
                        db.add(
                            ExplanationCard(
                                stock_id=candidate.stock.id,
                                article_id=article.id,
                                theme_id=article.themes[0].id if article.themes else None,
                                cluster_id=cluster.id,
                                title=explanation["title"],
                                summary_ko=explanation["summary"],
                                bullets_ko=explanation["bullets"],
                                evidence=[{"type": "article", "title": article.title, "published_at": article.published_at.isoformat()}],
                                risk_flags=explanation["risk_flags"],
                                confidence=explanation["confidence"],
                            )
                        )

                if article.source_type == SourceType.FOREIGN:
                    db.add(
                        ForeignNewsImpact(
                            article_id=article.id,
                            origin_region="US",
                            origin_market="미국",
                            translated_summary_ko=article.translated_summary_ko or article.summary,
                            korea_market_impact_summary=normalized.metadata.get("impact_summary")
                            or "해외 이벤트가 국내 공급망과 테마에 어떤 파급을 주는지 해석한 문장입니다.",
                            affected_themes=[theme.slug for theme in article.themes],
                            affected_stocks=normalized.metadata.get("related_tickers", []),
                            impact_confidence=min(article.relevance_score + 0.08, 0.96),
                        )
                    )

        self.ranking_engine.rebuild_snapshots(db)
        self.forecast_engine.rebuild_forecasts(db)
        db.commit()
        return {
            "processed_at": processed_at.isoformat(),
            "articles_seen": articles_seen,
            "articles_stored": stored,
            "relevant_articles": relevant,
            "providers": provider_statuses,
        }

    def _as_utc_naive(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value
        return value.astimezone(UTC).replace(tzinfo=None)
