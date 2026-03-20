from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin, articles, clusters, dashboard, health, stocks, themes
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.init_db import init_db
from app.db.session import get_session_factory
from app.services.pipeline.seed import SeedService

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level)
    init_db()
    if settings.enable_mock_seed_on_startup:
        session = get_session_factory()()
        try:
            SeedService().seed_all(session, force_reset=False)
        finally:
            session.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
app.include_router(themes.router, prefix=settings.api_prefix)
app.include_router(articles.router, prefix=settings.api_prefix)
app.include_router(clusters.router, prefix=settings.api_prefix)
app.include_router(stocks.router, prefix=settings.api_prefix)
app.include_router(admin.router, prefix=settings.api_prefix)

