from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import ArticleDetailResponseSchema, NewsCardSchema
from app.services.articles import ArticleService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=list[NewsCardSchema])
def list_articles(db: Session = Depends(get_db)):
    return ArticleService(db).list_articles()


@router.get("/{article_id}", response_model=ArticleDetailResponseSchema)
def get_article(article_id: UUID, db: Session = Depends(get_db)):
    response = ArticleService(db).get_article_detail(article_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return response

