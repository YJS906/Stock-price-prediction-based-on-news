import json

from app.core.config import get_settings
from app.core.enums import SourceType
from app.services.pipeline.providers.base import NewsProvider


class MockDomesticNewsProvider(NewsProvider):
    name = "mock-domestic"
    source_type = SourceType.DOMESTIC

    def fetch(self) -> list[dict]:
        payload = json.loads((get_settings().shared_data_path / "mock-seed.json").read_text(encoding="utf-8"))
        return [item for item in payload["articles"] if item["source_type"] == SourceType.DOMESTIC.value]

