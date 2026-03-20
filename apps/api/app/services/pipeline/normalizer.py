import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.core.enums import MarketScope, SourceType


@dataclass(slots=True)
class NormalizedArticle:
    provider: str
    source_type: SourceType
    source_name: str
    external_id: str | None
    url: str
    title: str
    summary: str
    body: str | None
    translated_summary_ko: str | None
    published_at: datetime
    language: str
    authors: list[str]
    image_url: str | None
    symbols_hint: list[str]
    dedupe_hash: str
    market_scope: MarketScope
    metadata: dict[str, Any]


class ArticleNormalizer:
    def normalize(self, raw: dict[str, Any]) -> NormalizedArticle:
        dedupe_source = f"{raw.get('title', '').strip().lower()}::{raw.get('url', '').strip().lower()}"
        dedupe_hash = hashlib.sha256(dedupe_source.encode("utf-8")).hexdigest()
        published_at = datetime.fromisoformat(raw["published_at"])
        market_scope = MarketScope.MIXED if raw["source_type"] == SourceType.FOREIGN.value else MarketScope.KOREA

        return NormalizedArticle(
            provider=raw["provider"],
            source_type=SourceType(raw["source_type"]),
            source_name=raw["source_name"],
            external_id=raw.get("external_id"),
            url=raw["url"],
            title=raw["title"].strip(),
            summary=raw["summary"].strip(),
            body=raw.get("body"),
            translated_summary_ko=raw.get("translated_summary_ko"),
            published_at=published_at,
            language=raw.get("language", "ko"),
            authors=raw.get("authors", []),
            image_url=raw.get("image_url"),
            symbols_hint=raw.get("related_tickers", []),
            dedupe_hash=dedupe_hash,
            market_scope=market_scope,
            metadata={
                "cluster_key": raw.get("cluster_key"),
                "cluster_headline": raw.get("cluster_headline"),
                "theme_hints": raw.get("themes", []),
                "related_tickers": raw.get("related_tickers", []),
                "impact_summary": raw.get("korea_market_impact_summary"),
            },
        )

