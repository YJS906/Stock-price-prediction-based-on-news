from app.db.session import get_session_factory
from app.services.pipeline.seed import SeedService
from app.tasks.celery_app import celery_app


@celery_app.task(name="newsalpha.seed_refresh")
def seed_refresh(force_reset: bool = False) -> dict:
    session = get_session_factory()()
    try:
        return SeedService().seed_all(session, force_reset=force_reset)
    finally:
        session.close()

