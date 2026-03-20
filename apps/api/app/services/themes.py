from sqlalchemy.orm import Session

from app.repositories.theme import ThemeRepository
from app.schemas.api import ThemeCardSchema, ThemeDetailResponseSchema
from app.services.presenters import cluster_card, news_card, ranking_entry, theme_card


class ThemeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ThemeRepository(db)

    def list_themes(self) -> list[ThemeCardSchema]:
        themes = self.repo.list_themes()
        ordered = sorted(themes, key=lambda item: len(item.articles), reverse=True)
        return [ThemeCardSchema(**theme_card(theme)) for theme in ordered]

    def get_theme_detail(self, slug: str) -> ThemeDetailResponseSchema | None:
        theme = self.repo.get_by_slug(slug)
        if theme is None:
            return None

        snapshot = self.repo.get_snapshot(theme.id)
        articles = self.repo.list_articles_for_theme(theme.id)
        clusters = []
        cluster_seen = set()
        for article in articles:
            for cluster in article.clusters:
                if cluster.id in cluster_seen:
                    continue
                clusters.append(cluster)
                cluster_seen.add(cluster.id)

        stock_map = {link.stock.ticker: link.stock for link in theme.stocks}
        ranking = [ranking_entry(item, stock_map) for item in (snapshot.items if snapshot else []) if item["ticker"] in stock_map]

        return ThemeDetailResponseSchema(
            theme=ThemeCardSchema(**theme_card(theme)),
            clusters=[cluster_card(cluster) for cluster in sorted(clusters, key=lambda item: item.latest_published_at, reverse=True)],
            articles=[news_card(article) for article in articles],
            ranking=ranking,
        )

