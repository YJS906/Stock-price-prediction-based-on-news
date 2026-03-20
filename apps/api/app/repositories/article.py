from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Article, StockNewsLink


class ArticleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_articles(self, limit: int = 30) -> list[Article]:
        statement = (
            select(Article)
            .where(Article.is_stock_relevant.is_(True))
            .options(
                selectinload(Article.themes),
                selectinload(Article.stock_links).selectinload(StockNewsLink.stock),
                selectinload(Article.foreign_impact),
                selectinload(Article.clusters),
            )
            .order_by(Article.published_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

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
