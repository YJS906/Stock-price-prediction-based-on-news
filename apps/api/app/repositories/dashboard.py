from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import RankingScope
from app.models import Article, ArticleCluster, RankingSnapshot, StockNewsLink, StockThemeLink, Theme


class DashboardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active_themes(self) -> list[Theme]:
        statement = (
            select(Theme)
            .where(Theme.is_active.is_(True))
            .options(selectinload(Theme.articles), selectinload(Theme.stocks).selectinload(StockThemeLink.stock))
            .order_by(Theme.name_ko.asc())
        )
        return list(self.db.scalars(statement).all())

    def list_latest_articles(self, limit: int = 10) -> list[Article]:
        base_statement = (
            select(Article)
            .where(Article.is_stock_relevant.is_(True))
            .options(
                selectinload(Article.themes),
                selectinload(Article.stock_links).selectinload(StockNewsLink.stock),
                selectinload(Article.foreign_impact),
            )
        )
        live_statement = base_statement.where(~Article.provider.like("mock-%")).order_by(Article.published_at.desc()).limit(limit)
        live_articles = list(self.db.scalars(live_statement).all())
        if live_articles:
            return live_articles

        fallback_statement = base_statement.order_by(Article.published_at.desc()).limit(limit)
        return list(self.db.scalars(fallback_statement).all())

    def list_hot_clusters(self, limit: int = 5) -> list[ArticleCluster]:
        statement = (
            select(ArticleCluster)
            .options(selectinload(ArticleCluster.articles))
            .order_by(ArticleCluster.latest_published_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def get_dashboard_snapshot(self) -> RankingSnapshot | None:
        statement = select(RankingSnapshot).where(RankingSnapshot.scope_type == RankingScope.DASHBOARD)
        return self.db.scalar(statement)
