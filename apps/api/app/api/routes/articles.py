from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import ArticleDetailResponseSchema, LiveNewsResponseSchema, NewsCardSchema
from app.services.articles import ArticleService
from app.services.realtime import LiveFeedService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=list[NewsCardSchema])
def list_articles(theme: str | None = Query(default=None), db: Session = Depends(get_db)):
    return ArticleService(db).list_articles(theme_slug=theme)


@router.get("/live", response_model=LiveNewsResponseSchema)
def get_live_articles(
    theme: str | None = Query(default=None),
    limit: int = Query(default=20, ge=5, le=50),
    db: Session = Depends(get_db),
):
    return LiveFeedService(db).get_live_feed(theme_slug=theme, limit=limit)


@router.get("/{article_id}", response_model=ArticleDetailResponseSchema)
def get_article(article_id: UUID, db: Session = Depends(get_db)):
    response = ArticleService(db).get_article_detail(article_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return response
