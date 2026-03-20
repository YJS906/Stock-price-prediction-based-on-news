from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Article, Stock, StockNewsLink, StockThemeLink


class StockRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_stocks(self, query: str | None = None, limit: int = 25) -> list[Stock]:
        statement = select(Stock).options(
            selectinload(Stock.themes).selectinload(StockThemeLink.theme),
            selectinload(Stock.prices),
            selectinload(Stock.forecasts),
        )
        if query:
            pattern = f"%{query}%"
            statement = statement.where(or_(Stock.ticker.like(pattern), Stock.name_ko.like(pattern), Stock.name_en.like(pattern)))
        statement = statement.order_by(Stock.name_ko.asc()).limit(limit)
        return list(self.db.scalars(statement).all())

    def get_by_ticker(self, ticker: str) -> Stock | None:
        statement = (
            select(Stock)
            .where(Stock.ticker == ticker)
            .options(
                selectinload(Stock.themes).selectinload(StockThemeLink.theme),
                selectinload(Stock.news_links).selectinload(StockNewsLink.article).selectinload(Article.themes),
                selectinload(Stock.prices),
                selectinload(Stock.forecasts),
                selectinload(Stock.explanations),
            )
        )
        return self.db.scalar(statement)
