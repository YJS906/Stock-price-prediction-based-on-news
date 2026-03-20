from datetime import UTC, datetime, timedelta
from threading import Lock

from sqlalchemy.orm import Session

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

    def get_live_feed(self, theme_slug: str | None = None, limit: int = 20) -> LiveNewsResponseSchema:
        self._refresh_if_due()
        items = self.article_service.list_articles(theme_slug=theme_slug)[:limit]
        return LiveNewsResponseSchema(
            generatedAt=datetime.now(UTC).isoformat(),
            pollingIntervalMs=self.polling_interval_ms,
            themeSlug=theme_slug,
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
                return
