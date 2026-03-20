from app.core.enums import SourceType
from app.services.pipeline.providers.base import NewsProvider
from app.services.pipeline.providers.mock_release import released_mock_articles


class MockForeignNewsProvider(NewsProvider):
    name = "mock-foreign"
    source_type = SourceType.FOREIGN

    def fetch(self) -> list[dict]:
        return released_mock_articles(self.source_type)
