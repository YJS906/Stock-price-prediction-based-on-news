from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.enums import ForecastHorizon, RankingScope
from app.models import Forecast, MarketPrice, RankingSnapshot, Stock
from app.services.market_data import NaverMarketDataService, candle_rows_for_storage


class ForecastEngine:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.market_data = NaverMarketDataService()

    def rebuild_market_prices(self, db: Session) -> None:
        db.execute(delete(MarketPrice))
        if self.settings.market_data_provider_mode.lower() != "mock":
            if self._rebuild_live_market_prices(db):
                return

        self._rebuild_mock_market_prices(db)

    def _rebuild_live_market_prices(self, db: Session) -> bool:
        stored = 0
        for stock in db.scalars(select(Stock)).all():
            payload = self.market_data.fetch(stock.ticker)
            if not payload:
                continue

            for candle in candle_rows_for_storage(payload):
                db.add(
                    MarketPrice(
                        stock_id=stock.id,
                        bucket_at=candle["bucket_at"],
                        timeframe=candle["timeframe"],
                        open=round(candle["open"], 2),
                        high=round(candle["high"], 2),
                        low=round(candle["low"], 2),
                        close=round(candle["close"], 2),
                        volume=int(candle["volume"]),
                        source=candle["source"],
                        extra={
                            **(candle.get("extra") or {}),
                            "updated_at": payload["updated_at"],
                            "timeframe": payload["timeframe"],
                        },
                    )
                )
                stored += 1
        return stored > 0

    def _rebuild_mock_market_prices(self, db: Session) -> None:
        now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
        seeds = {
            "000660": 182000,
            "042700": 126400,
            "007660": 46400,
            "012450": 292500,
            "079550": 188900,
            "010120": 238500,
            "267260": 358000,
            "034020": 30100,
            "247540": 193500,
            "006400": 408000,
            "207940": 956000,
            "277810": 261000,
        }

        for stock in db.scalars(select(Stock)).all():
            base = seeds.get(stock.ticker, 50000)
            drift = ((sum(ord(char) for char in stock.ticker) % 11) - 5) / 1000
            for step in range(24):
                bucket_at = now - timedelta(hours=23 - step)
                open_price = round(base * (1 + drift * step / 4), 2)
                close_price = round(open_price * (1 + drift + ((step % 3) - 1) * 0.002), 2)
                high_price = max(open_price, close_price) * 1.006
                low_price = min(open_price, close_price) * 0.995
                db.add(
                    MarketPrice(
                        stock_id=stock.id,
                        bucket_at=bucket_at,
                        timeframe="1h",
                        open=open_price,
                        high=round(high_price, 2),
                        low=round(low_price, 2),
                        close=close_price,
                        volume=80000 + step * 1250,
                        extra={"session": "mock"},
                    )
                )

    def rebuild_forecasts(self, db: Session) -> None:
        db.execute(delete(Forecast))
        dashboard_snapshot = db.scalar(select(RankingSnapshot).where(RankingSnapshot.scope_type == RankingScope.DASHBOARD))
        ranking_lookup = {item["ticker"]: item for item in (dashboard_snapshot.items if dashboard_snapshot else [])}

        for stock in db.scalars(select(Stock)).all():
            candles = db.scalars(
                select(MarketPrice).where(MarketPrice.stock_id == stock.id).order_by(MarketPrice.bucket_at.asc())
            ).all()
            if len(candles) < 2:
                continue

            last_close = candles[-1].close
            prev_close = candles[-2].close
            momentum = (last_close - prev_close) / prev_close if prev_close else 0.0
            ranking = ranking_lookup.get(stock.ticker, {"upside_score": 0.48, "relevance_score": 0.42})

            up_prob = min(max(0.44 + momentum * 3 + ranking["upside_score"] * 0.28, 0.12), 0.88)
            down_prob = min(max(0.24 - momentum * 2 + (0.55 - ranking["relevance_score"]) * 0.18, 0.08), 0.66)
            neutral = max(1 - up_prob - down_prob, 0.1)
            scale = up_prob + down_prob + neutral
            up_prob, down_prob, neutral = [round(value / scale, 4) for value in (up_prob, down_prob, neutral)]

            band_width = last_close * (0.012 + (1 - ranking["relevance_score"]) * 0.01)
            intraday = [
                {
                    "label": "09:00-10:30",
                    "bullish": round(min(up_prob + 0.04, 0.92), 4),
                    "neutral": round(neutral, 4),
                    "bearish": round(max(down_prob - 0.03, 0.04), 4),
                },
                {
                    "label": "10:30-13:30",
                    "bullish": round(up_prob, 4),
                    "neutral": round(neutral + 0.02, 4),
                    "bearish": round(max(down_prob - 0.02, 0.05), 4),
                },
                {
                    "label": "13:30-15:30",
                    "bullish": round(max(up_prob - 0.03, 0.05), 4),
                    "neutral": round(neutral + 0.01, 4),
                    "bearish": round(min(down_prob + 0.03, 0.9), 4),
                },
            ]

            db.add(
                Forecast(
                    stock_id=stock.id,
                    theme_id=None,
                    cluster_id=None,
                    forecast_horizon=ForecastHorizon.CLOSE,
                    direction_up_prob=up_prob,
                    direction_flat_prob=neutral,
                    direction_down_prob=down_prob,
                    predicted_close_low=round(last_close - band_width, 2),
                    predicted_close_base=round(last_close * (1 + (up_prob - down_prob) * 0.018), 2),
                    predicted_close_high=round(last_close + band_width, 2),
                    intraday_path=intraday,
                    confidence_interval={"p10": round(last_close - band_width, 2), "p90": round(last_close + band_width, 2)},
                    feature_snapshot={
                        "momentum": round(momentum, 4),
                        "ranking_score": ranking["upside_score"],
                        "relevance_score": ranking["relevance_score"],
                    },
                    generated_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(hours=6),
                )
            )
