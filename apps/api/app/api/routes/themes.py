from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import ThemeCardSchema, ThemeDetailResponseSchema
from app.services.themes import ThemeService

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("", response_model=list[ThemeCardSchema])
def list_themes(db: Session = Depends(get_db)):
    return ThemeService(db).list_themes()


@router.get("/{theme_slug}", response_model=ThemeDetailResponseSchema)
def get_theme_detail(theme_slug: str, db: Session = Depends(get_db)):
    response = ThemeService(db).get_theme_detail(theme_slug)
    if response is None:
        raise HTTPException(status_code=404, detail="Theme not found")
    return response

