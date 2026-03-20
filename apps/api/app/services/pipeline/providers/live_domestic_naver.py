from datetime import UTC, datetime
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.core.enums import SourceType
from app.services.pipeline.providers.base import NewsProvider


class LiveDomesticNaverNewsProvider(NewsProvider):
    name = "live-domestic-naver"
    source_type = SourceType.DOMESTIC
    base_url = "https://finance.naver.com/news/mainnews.naver"
    site_root = "https://finance.naver.com"
    korea_tz = ZoneInfo("Asia/Seoul")

    def fetch(self) -> list[dict]:
        settings = get_settings()
        client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
            },
            timeout=10.0,
            follow_redirects=True,
        )
        articles: list[dict] = []
        seen_urls: set[str] = set()

        with client:
            for page in range(1, settings.live_domestic_news_pages + 1):
                response = client.get(self.base_url, params={"page": page})
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                for item in soup.select("ul.newsList li"):
                    anchor = item.select_one("dd.articleSubject a")
                    summary_node = item.select_one("dd.articleSummary")
                    if anchor is None or summary_node is None:
                        continue

                    raw_url = anchor.get("href", "").strip()
                    if not raw_url:
                        continue
                    article_url = urljoin(self.site_root, raw_url)
                    if article_url in seen_urls:
                        continue

                    title = anchor.get_text(" ", strip=True)
                    source_name = self._press_name(summary_node)
                    published_at = self._parse_datetime(self._published_text(summary_node))
                    summary = self._summary_text(summary_node)
                    published_at_iso = published_at.astimezone(UTC).isoformat()
                    external_id = self._external_id(raw_url)

                    seen_urls.add(article_url)
                    articles.append(
                        {
                            "provider": self.name,
                            "source_type": self.source_type.value,
                            "source_name": source_name,
                            "external_id": external_id,
                            "url": article_url,
                            "title": title,
                            "summary": summary or title,
                            "body": None,
                            "translated_summary_ko": None,
                            "published_at": published_at_iso,
                            "language": "ko",
                            "authors": [],
                            "image_url": None,
                            "related_tickers": [],
                            "themes": [],
                            "cluster_key": f"naver:{external_id}",
                            "cluster_headline": title,
                        }
                    )

        return articles

    def _press_name(self, summary_node) -> str:
        press_node = summary_node.select_one("span.press")
        return press_node.get_text(" ", strip=True)[:80] if press_node else "네이버 금융"

    def _published_text(self, summary_node) -> str:
        time_node = summary_node.select_one("span.wdate")
        return time_node.get_text(" ", strip=True) if time_node else ""

    def _summary_text(self, summary_node) -> str:
        cloned = BeautifulSoup(str(summary_node), "html.parser")
        for node in cloned.select("span.press, span.bar, span.wdate"):
            node.decompose()
        text = cloned.get_text(" ", strip=True)
        return " ".join(text.split())

    def _parse_datetime(self, date_text: str) -> datetime:
        cleaned = date_text.replace(".", "-").strip()
        try:
            return datetime.strptime(cleaned, "%Y-%m-%d %H:%M").replace(tzinfo=self.korea_tz).astimezone(UTC)
        except ValueError:
            return datetime.now(UTC)

    def _external_id(self, raw_url: str) -> str:
        article_id = raw_url.split("article_id=")[-1].split("&", 1)[0] if "article_id=" in raw_url else raw_url
        office_id = raw_url.split("office_id=")[-1].split("&", 1)[0] if "office_id=" in raw_url else "naver"
        return f"{office_id}:{article_id}"[:120]
