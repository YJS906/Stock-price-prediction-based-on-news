import hashlib
from datetime import UTC, datetime
from html import unescape
from urllib.parse import quote_plus

import feedparser
import httpx
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

from app.core.config import get_settings
from app.core.enums import SourceType
from app.services.pipeline.providers.base import NewsProvider


class LiveForeignGoogleNewsProvider(NewsProvider):
    name = "live-foreign-google"
    source_type = SourceType.FOREIGN

    theme_hint_map = {
        "ai-infrastructure": ["ai", "nvidia", "semiconductor", "hbm", "server", "memory", "chip"],
        "power-grid-nuclear": ["grid", "power", "nuclear", "utility", "transformer", "data center power"],
        "secondary-battery": ["battery", "ev", "cathode", "energy storage"],
        "biopharma-cdmo": ["biotech", "drug", "cdmo", "manufacturing"],
        "robotics-smartfactory": ["robot", "automation", "factory"],
        "defense-space": ["defense", "missile", "satellite", "artillery"],
    }

    def fetch(self) -> list[dict]:
        settings = get_settings()
        query = quote_plus(settings.live_foreign_news_query)
        feed_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

        response = httpx.get(
            feed_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10.0,
            follow_redirects=True,
        )
        response.raise_for_status()
        parsed = feedparser.parse(response.text)
        entries = parsed.entries[: settings.live_foreign_news_max_items]
        articles: list[dict] = []

        for entry in entries:
            title = self._clean_title(getattr(entry, "title", ""))
            summary = self._summary_from_entry(entry, title)
            translated = self._translate_to_korean(summary)
            published_at = self._published_at(entry)
            themes = self._theme_hints(f"{title} {summary}")
            link = getattr(entry, "link", "")
            raw_identifier = getattr(entry, "id", None) or link or title
            external_id = f"google:{hashlib.sha1(raw_identifier.encode('utf-8')).hexdigest()[:32]}"

            articles.append(
                {
                    "provider": self.name,
                    "source_type": self.source_type.value,
                    "source_name": getattr(getattr(entry, "source", None), "title", None) or "Google News",
                    "external_id": external_id,
                    "url": link,
                    "original_url": None,
                    "source_home_url": getattr(getattr(entry, "source", None), "href", None),
                    "title": title,
                    "summary": summary,
                    "body": None,
                    "translated_summary_ko": translated,
                    "published_at": published_at.isoformat(),
                    "language": "en",
                    "authors": [],
                    "image_url": None,
                    "related_tickers": [],
                    "themes": themes,
                    "cluster_key": f"google:{hashlib.sha1(raw_identifier.encode('utf-8')).hexdigest()[:16]}",
                    "cluster_headline": title,
                    "korea_market_impact_summary": self._impact_summary(themes, translated or summary),
                }
            )

        return articles

    def _clean_title(self, raw: str) -> str:
        title = unescape(raw).strip()
        if " - " in title:
            title = title.rsplit(" - ", 1)[0].strip()
        return title

    def _summary_from_entry(self, entry, title: str) -> str:
        summary_html = getattr(entry, "summary", "") or getattr(entry, "description", "")
        if not summary_html:
            return title
        text = BeautifulSoup(summary_html, "html.parser").get_text(" ", strip=True)
        normalized = " ".join(text.split())
        return normalized or title

    def _translate_to_korean(self, text: str) -> str | None:
        cleaned = text.strip()
        if not cleaned:
            return None
        try:
            return GoogleTranslator(source="auto", target="ko").translate(cleaned)
        except Exception:
            return None

    def _published_at(self, entry) -> datetime:
        raw = getattr(entry, "published", None) or getattr(entry, "updated", None)
        if not raw:
            return datetime.now(UTC)
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=UTC)
        except Exception:
            return datetime.now(UTC)

    def _theme_hints(self, text: str) -> list[str]:
        normalized = text.lower()
        matched = []
        for slug, keywords in self.theme_hint_map.items():
            if any(keyword in normalized for keyword in keywords):
                matched.append(slug)
        return matched

    def _impact_summary(self, themes: list[str], translated_summary: str) -> str:
        if "ai-infrastructure" in themes:
            return "미국 AI·반도체 뉴스는 국내 HBM, 패키징, 전력 인프라 관련주에 수급 기대를 확산시킬 수 있습니다."
        if "power-grid-nuclear" in themes:
            return "미국 전력망·원전 이슈는 국내 변압기, 송배전, 원전 밸류체인 종목의 테마 강도에 영향을 줄 수 있습니다."
        if "secondary-battery" in themes:
            return "미국 배터리·에너지저장장치 뉴스는 국내 2차전지 소재와 장비주의 단기 기대감에 연결될 수 있습니다."
        if "defense-space" in themes:
            return "해외 방산 수요 확대 뉴스는 국내 방산 수출주와 우주항공 테마의 모멘텀 해석에 활용될 수 있습니다."
        return f"해외 주요 뉴스가 국내 증시 테마에 미치는 파급 가능성을 요약한 내용입니다. {translated_summary[:120]}"
