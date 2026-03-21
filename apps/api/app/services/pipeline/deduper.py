from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Article
from app.services.pipeline.normalizer import NormalizedArticle


class ArticleDeduper:
    def is_duplicate(self, db: Session, article: NormalizedArticle) -> bool:
        conditions = [Article.dedupe_hash == article.dedupe_hash]

        if article.url:
            conditions.append(Article.url == article.url)

        if article.external_id:
            conditions.append((Article.provider == article.provider) & (Article.external_id == article.external_id))

        statement = select(Article.id).where(or_(*conditions))
        return db.execute(statement).scalar_one_or_none() is not None
