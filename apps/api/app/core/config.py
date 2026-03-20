from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "NewsAlpha API"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    timezone: str = "Asia/Seoul"
    database_url: str = "sqlite+pysqlite:///./newsalpha.db"
    redis_url: str = "redis://redis:6379/0"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://web:3000",
        ]
    )
    enable_mock_seed_on_startup: bool = True
    log_level: str = "INFO"
    news_provider_mode: str = "hybrid"
    market_data_provider_mode: str = "live"
    live_domestic_news_pages: int = 2
    live_foreign_news_max_items: int = 12
    live_foreign_news_query: str = "US stocks OR semiconductor OR AI server OR Nvidia OR data center power"

    @property
    def repo_root(self) -> Path:
        return Path(__file__).resolve().parents[4]

    @property
    def shared_data_path(self) -> Path:
        return self.repo_root / "packages" / "shared" / "data"

    @property
    def ml_reports_path(self) -> Path:
        return self.repo_root / "ml" / "src" / "newsalpha_ml" / "evaluation" / "reports.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
