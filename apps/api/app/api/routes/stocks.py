from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import ForecastWidgetSchema, StockDetailResponseSchema, TimelineItemSchema
from app.services.stocks import StockService

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("")
def list_stocks(q: str | None = Query(default=None), db: Session = Depends(get_db)):
    return StockService(db).list_stocks(query=q)


@router.get("/{ticker}", response_model=StockDetailResponseSchema)
def get_stock_detail(ticker: str, db: Session = Depends(get_db)):
    response = StockService(db).get_stock_detail(ticker)
    if response is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return response


@router.get("/{ticker}/forecast", response_model=ForecastWidgetSchema)
def get_stock_forecast(ticker: str, db: Session = Depends(get_db)):
    response = StockService(db).get_stock_forecast(ticker)
    if response is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return response


@router.get("/{ticker}/timeline", response_model=list[TimelineItemSchema])
def get_stock_timeline(ticker: str, db: Session = Depends(get_db)):
    response = StockService(db).get_stock_timeline(ticker)
    if response is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return response

