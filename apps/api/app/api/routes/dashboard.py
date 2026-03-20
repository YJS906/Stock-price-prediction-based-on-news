from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import DashboardResponseSchema
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponseSchema)
def get_dashboard(db: Session = Depends(get_db)):
    return DashboardService(db).get_dashboard()

