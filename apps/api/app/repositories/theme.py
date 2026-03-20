from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import RankingScope
from app.models import Article, RankingSnapshot, StockNewsLink, StockThemeLink, Theme


class ThemeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_themes(self) -> list[Theme]:
        statement = (
            select(Theme)
            .where(Theme.is_active.is_(True))
            .options(selectinload(Theme.articles), selectinload(Theme.stocks))
            .order_by(Theme.name_ko.asc())
        )
        return list(self.db.scalars(statement).all())

    def get_by_slug(self, slug: str) -> Theme | None:
        statement = (
            select(Theme)
            .where(Theme.slug == slug)
            .options(selectinload(Theme.articles), selectinload(Theme.stocks).selectinload(StockThemeLink.stock))
        )
        return self.db.scalar(statement)

    def get_snapshot(self, theme_id) -> RankingSnapshot | None:
        statement = select(RankingSnapshot).where(
            RankingSnapshot.scope_type == RankingScope.THEME,
            RankingSnapshot.scope_id == theme_id,
        )
        return self.db.scalar(statement)

    def list_articles_for_theme(self, theme_id, limit: int = 12) -> list[Article]:
        statement = (
            select(Article)
            .join(Article.themes)
            .where(Theme.id == theme_id)
            .options(
                selectinload(Article.themes),
                selectinload(Article.stock_links).selectinload(StockNewsLink.stock),
                selectinload(Article.clusters),
            )
            .order_by(Article.published_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(statement).unique().all())
