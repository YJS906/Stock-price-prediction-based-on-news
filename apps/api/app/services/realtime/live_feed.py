from datetime import UTC, datetime, timedelta
from threading import Lock

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.schemas.api import LiveNewsResponseSchema
from app.services.articles import ArticleService
from app.services.pipeline.seed import SeedService

_refresh_lock = Lock()
_last_refresh_attempt_at: datetime | None = None


class LiveFeedService:
    polling_interval_ms = 10000
    ingest_throttle_seconds = 15

    def __init__(self, db: Session) -> None:
        self.db = db
        self.article_service = ArticleService(db)
        self.seed_service = SeedService()
        self.settings = get_settings()

    def get_live_feed(self, theme_slug: str | None = None, limit: int = 20) -> LiveNewsResponseSchema:
        self._refresh_if_due()
        items = self.article_service.list_articles(theme_slug=theme_slug)[:limit]
        content_mode = self._content_mode(items)
        return LiveNewsResponseSchema(
            generatedAt=datetime.now(UTC).isoformat(),
            pollingIntervalMs=self.polling_interval_ms,
            newestPublishedAt=items[0]["publishedAt"] if items else None,
            themeSlug=theme_slug,
            timezone=self.settings.timezone,
            connectionMode="polling",
            contentMode=content_mode,
            items=items,
        )

    def _refresh_if_due(self) -> None:
        global _last_refresh_attempt_at

        now = datetime.now(UTC)
        if _last_refresh_attempt_at and now - _last_refresh_attempt_at < timedelta(seconds=self.ingest_throttle_seconds):
            return

        with _refresh_lock:
            now = datetime.now(UTC)
            if _last_refresh_attempt_at and now - _last_refresh_attempt_at < timedelta(seconds=self.ingest_throttle_seconds):
                return

            _last_refresh_attempt_at = now
            try:
                self.seed_service.refresh_news(self.db)
            except Exception:
                # Keep the live feed readable even if a provider fetch fails.
                self.db.rollback()
                return

    def _content_mode(self, items: list[dict]) -> str:
        configured = self.settings.news_provider_mode.lower()
        if configured == "mock":
            return "mock"
        if configured == "live":
            return "live"
        if not items:
            return "hybrid"
        if all(item.get("contentMode") == "live" for item in items):
            return "live"
        if all(item.get("contentMode") == "mock" for item in items):
            return "mock"
        return "hybrid"
