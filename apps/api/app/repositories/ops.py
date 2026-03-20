from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Article


class OpsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def article_counts(self) -> tuple[int, int]:
        total = self.db.scalar(select(func.count(Article.id))) or 0
        relevant = self.db.scalar(select(func.count(Article.id)).where(Article.is_stock_relevant.is_(True))) or 0
        return total, relevant

    def last_ingested_at(self):
        return self.db.scalar(select(func.max(Article.created_at)))

