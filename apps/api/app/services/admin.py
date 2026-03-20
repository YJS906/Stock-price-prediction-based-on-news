from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.ops import OpsRepository
from app.services.pipeline.provider_registry import configured_provider_statuses
from app.services.pipeline.seed import SeedService


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OpsRepository(db)
        self.seed_service = SeedService()

    def pipeline_status(self):
        total, relevant = self.repo.article_counts()
        last_ingested = self.repo.last_ingested_at() or datetime.utcnow()
        rate = round(relevant / max(total, 1), 4)
        providers = [
            {
                **provider,
                "status": "healthy",
                "lastFetchedAt": last_ingested.isoformat(),
            }
            for provider in configured_provider_statuses()
        ]
        return {
            "lastIngestedAt": last_ingested.isoformat(),
            "articlesSeen": total,
            "articlesStored": total,
            "stockRelevantRate": rate,
            "queueDepth": 0,
            "workerStatus": "idle",
            "providers": providers,
        }

    def run_ingest(self):
        payload = self.seed_service.seed_all(self.db, force_reset=False)
        return {"status": "ok", "detail": "Ingest completed", "payload": payload}

    def reset_seed(self):
        payload = self.seed_service.seed_all(self.db, force_reset=True)
        return {"status": "ok", "detail": "Database reset and reseeded", "payload": payload}
