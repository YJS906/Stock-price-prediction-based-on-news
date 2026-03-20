from app.core.config import get_settings
from app.services.pipeline.providers.base import NewsProvider
from app.services.pipeline.providers.live_domestic_naver import LiveDomesticNaverNewsProvider
from app.services.pipeline.providers.live_foreign_google import LiveForeignGoogleNewsProvider
from app.services.pipeline.providers.mock_domestic import MockDomesticNewsProvider
from app.services.pipeline.providers.mock_foreign import MockForeignNewsProvider


def live_news_providers() -> list[NewsProvider]:
    return [LiveDomesticNaverNewsProvider(), LiveForeignGoogleNewsProvider()]


def mock_news_providers() -> list[NewsProvider]:
    return [MockDomesticNewsProvider(), MockForeignNewsProvider()]


def provider_groups() -> list[list[NewsProvider]]:
    settings = get_settings()
    mode = settings.news_provider_mode.lower()
    if mode == "live":
        return [live_news_providers()]
    if mode == "mock":
        return [mock_news_providers()]
    return [live_news_providers(), mock_news_providers()]


def configured_provider_statuses() -> list[dict[str, str]]:
    statuses = []
    for group in provider_groups():
        for provider in group:
            statuses.append(
                {
                    "name": provider.name,
                    "kind": provider.source_type.value,
                }
            )
    unique: dict[str, dict[str, str]] = {}
    for item in statuses:
        unique[item["name"]] = item
    return list(unique.values())
