from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Article
from app.services.pipeline.normalizer import NormalizedArticle


class ArticleDeduper:
    def is_duplicate(self, db: Session, article: NormalizedArticle) -> bool:
        statement = select(Article.id).where(Article.dedupe_hash == article.dedupe_hash)
        return db.execute(statement).scalar_one_or_none() is not None

