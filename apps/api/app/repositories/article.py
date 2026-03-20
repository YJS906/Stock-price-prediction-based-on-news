from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Article, StockNewsLink, Theme


class ArticleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_articles(self, limit: int = 60) -> list[Article]:
        base_statement = (
            select(Article)
            .where(Article.is_stock_relevant.is_(True))
            .options(
                selectinload(Article.themes),
                selectinload(Article.stock_links).selectinload(StockNewsLink.stock),
                selectinload(Article.foreign_impact),
                selectinload(Article.clusters),
            )
        )
        live_statement = base_statement.where(~Article.provider.like("mock-%")).order_by(Article.published_at.desc()).limit(limit)
        live_articles = list(self.db.scalars(live_statement).all())
        if live_articles:
            return live_articles

        fallback_statement = base_statement.order_by(Article.published_at.desc()).limit(limit)
        return list(self.db.scalars(fallback_statement).all())

    def list_articles_by_theme(self, theme_slug: str, limit: int = 60) -> list[Article]:
        base_statement = (
            select(Article)
            .join(Article.themes)
            .where(Article.is_stock_relevant.is_(True), Theme.slug == theme_slug)
            .options(
                selectinload(Article.themes),
                selectinload(Article.stock_links).selectinload(StockNewsLink.stock),
                selectinload(Article.foreign_impact),
                selectinload(Article.clusters),
            )
        )
        live_statement = base_statement.where(~Article.provider.like("mock-%")).order_by(Article.published_at.desc()).limit(limit)
        live_articles = list(self.db.scalars(live_statement).unique().all())
        if live_articles:
            return live_articles

        fallback_statement = base_statement.order_by(Article.published_at.desc()).limit(limit)
        return list(self.db.scalars(fallback_statement).unique().all())

    def get_article(self, article_id: str) -> Article | None:
        statement = (
            select(Article)
            .where(Article.id == article_id)
            .options(
                selectinload(Article.themes),
                selectinload(Article.stock_links).selectinload(StockNewsLink.stock),
                selectinload(Article.foreign_impact),
                selectinload(Article.clusters),
            )
        )
        return self.db.scalar(statement)
