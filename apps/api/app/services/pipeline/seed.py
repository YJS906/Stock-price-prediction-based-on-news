import json

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.enums import MarketCode
from app.models import Forecast, MarketPrice, Stock, StockThemeLink, Theme
from app.services.pipeline.forecaster import ForecastEngine
from app.services.pipeline.providers.mock_release import reset_mock_feed_clock
from app.services.pipeline.ingest import IngestionPipelineService
from app.services.pipeline.provider_registry import provider_groups


class SeedService:
    theme_link_map = {
        "ai-infrastructure": ["000660", "042700", "007660", "010120"],
        "defense-space": ["012450", "079550"],
        "power-grid-nuclear": ["010120", "267260", "034020"],
        "secondary-battery": ["247540", "006400"],
        "biopharma-cdmo": ["207940"],
        "robotics-smartfactory": ["277810", "010120"],
    }

    def __init__(self) -> None:
        self.forecast_engine = ForecastEngine()
        self.pipeline = IngestionPipelineService()

    def reset_all(self, db: Session) -> None:
        self.pipeline.reset_generated_content(db)
        db.execute(delete(Forecast))
        db.execute(delete(MarketPrice))
        db.execute(delete(StockThemeLink))
        db.execute(delete(Stock))
        db.execute(delete(Theme))
        db.commit()

    def seed_reference(self, db: Session) -> None:
        payload = json.loads((get_settings().shared_data_path / "mock-seed.json").read_text(encoding="utf-8"))
        if db.scalar(select(Theme.id).limit(1)):
            return

        themes_by_slug: dict[str, Theme] = {}
        for raw in payload["themes"]:
            theme = Theme(
                slug=raw["slug"],
                name_ko=raw["name_ko"],
                name_en=raw.get("name_en"),
                description_ko=raw["description_ko"],
                description_en=raw.get("description_en"),
                market_regime=raw.get("market_regime", "neutral"),
                extra={},
            )
            db.add(theme)
            themes_by_slug[theme.slug] = theme

        stocks_by_ticker: dict[str, Stock] = {}
        for raw in payload["stocks"]:
            stock = Stock(
                ticker=raw["ticker"],
                name_ko=raw["name_ko"],
                name_en=raw.get("name_en"),
                market=MarketCode(raw["market"]),
                sector=raw["sector"],
                industry=raw["industry"],
                description=raw["description"],
                extra={"aliases": raw.get("aliases", [])},
            )
            db.add(stock)
            stocks_by_ticker[stock.ticker] = stock

        db.flush()

        for theme_slug, tickers in self.theme_link_map.items():
            theme = themes_by_slug[theme_slug]
            for ticker in tickers:
                stock = stocks_by_ticker[ticker]
                db.add(
                    StockThemeLink(
                        stock_id=stock.id,
                        theme_id=theme.id,
                        relation_type="core-beneficiary",
                        confidence=0.82,
                        supporting_entities=[theme.name_ko, stock.name_ko],
                        extra={},
                    )
                )

        db.commit()

    def seed_all(self, db: Session, force_reset: bool = False) -> dict:
        if force_reset:
            reset_mock_feed_clock()
            self.reset_all(db)

        self.seed_reference(db)
        self.forecast_engine.rebuild_market_prices(db)
        db.commit()
        return self.refresh_news(db)

    def refresh_news(self, db: Session) -> dict:
        self.seed_reference(db)
        last_payload: dict | None = None
        for providers in provider_groups():
            payload = self.pipeline.run(db, providers=providers)
            last_payload = payload
            if payload["articles_seen"] > 0 or get_settings().news_provider_mode.lower() != "hybrid":
                return payload
        return last_payload or {"processed_at": None, "articles_seen": 0, "articles_stored": 0, "relevant_articles": 0}
