import json
from copy import deepcopy
from datetime import UTC, datetime

from app.core.config import get_settings
from app.core.enums import SourceType

MOCK_FEED_BOOT_AT = datetime.now(UTC)
MOCK_BASE_RELEASE_COUNT = 3
MOCK_RELEASE_INTERVAL_SECONDS = 20


def reset_mock_feed_clock() -> None:
    global MOCK_FEED_BOOT_AT
    MOCK_FEED_BOOT_AT = datetime.now(UTC)


def released_mock_articles(source_type: SourceType) -> list[dict]:
    payload = json.loads((get_settings().shared_data_path / "mock-seed.json").read_text(encoding="utf-8"))
    candidates = [deepcopy(item) for item in payload["articles"] if item["source_type"] == source_type.value]
    visible_count = min(_visible_count(len(candidates)), len(candidates))
    visible_items = candidates[:visible_count]
    return visible_items


def _visible_count(total_count: int) -> int:
    elapsed_seconds = max((datetime.now(UTC) - MOCK_FEED_BOOT_AT).total_seconds(), 0)
    released = int(elapsed_seconds // MOCK_RELEASE_INTERVAL_SECONDS)
    return min(MOCK_BASE_RELEASE_COUNT + released, total_count)
