from datetime import UTC, datetime
from typing import Iterable
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

from app.models import Article, ArticleCluster, ExplanationCard, Forecast, MarketPrice, Stock, Theme

TIMEFRAME_ORDER = ("1m", "1d", "1w", "1mo")
KOREA_TIME_ZONE = ZoneInfo("Asia/Seoul")


def serialize_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(KOREA_TIME_ZONE).isoformat()


def _group_prices_by_timeframe(stock: Stock) -> dict[str, list[MarketPrice]]:
    grouped: dict[str, list[MarketPrice]] = {}
    for candle in stock.prices:
        grouped.setdefault(candle.timeframe, []).append(candle)
    for rows in grouped.values():
        rows.sort(key=lambda item: item.bucket_at)
    return grouped


def available_chart_timeframes(stock: Stock) -> list[str]:
    grouped = _group_prices_by_timeframe(stock)
    return [timeframe for timeframe in TIMEFRAME_ORDER if timeframe in grouped]


def default_chart_timeframe(stock: Stock) -> str:
    grouped = _group_prices_by_timeframe(stock)
    for timeframe in ("1d", "1w", "1mo", "1m"):
        if timeframe in grouped:
            return timeframe
    return "1d"


def _quote_timeframe(stock: Stock) -> str | None:
    grouped = _group_prices_by_timeframe(stock)
    for timeframe in ("1m", "1d", "1w", "1mo"):
        if timeframe in grouped:
            return timeframe
    return None


def _latest_candles(stock: Stock) -> tuple[MarketPrice | None, MarketPrice | None]:
    timeframe = _quote_timeframe(stock)
    if timeframe is None:
        return None, None
    rows = _group_prices_by_timeframe(stock).get(timeframe, [])
    if not rows:
        return None, None
    latest = rows[-1]
    previous = rows[-2] if len(rows) > 1 else latest
    return latest, previous


def _previous_close(stock: Stock) -> float:
    latest, previous = _latest_candles(stock)
    if latest and latest.extra and latest.extra.get("previous_close") is not None:
        return round(float(latest.extra["previous_close"]), 2)
    if previous:
        return round(previous.close, 2)
    return round(latest.close, 2) if latest else 0.0


def _day_change_pct(stock: Stock) -> float:
    latest, _ = _latest_candles(stock)
    previous_close = _previous_close(stock)
    if not latest or previous_close == 0:
        return 0.0
    return round(((latest.close - previous_close) / previous_close) * 100, 2)


def _current_price(stock: Stock) -> float:
    latest, _ = _latest_candles(stock)
    return round(latest.close, 2) if latest else 0.0


def price_status_from_source(source: str | None, session: str | None = None) -> str:
    if session == "mock" or (source or "").startswith("mock"):
        return "mock"
    if session == "live" or (source or "").startswith("naver"):
        return "live"
    return "delayed"


def quote_meta(stock: Stock) -> dict:
    timeframe = _quote_timeframe(stock)
    latest, _ = _latest_candles(stock)
    extra = latest.extra if latest and latest.extra else {}
    source = latest.source if latest else "mock-market"
    return {
        "priceTimeframe": timeframe or "1d",
        "priceSource": source,
        "priceStatus": price_status_from_source(source, extra.get("session")),
        "priceUpdatedAt": extra.get("updated_at") or serialize_datetime(latest.bucket_at if latest else None),
        "bestBid": extra.get("best_bid"),
        "bestAsk": extra.get("best_ask"),
    }


def price_disclaimer(price_status: str) -> str:
    if price_status == "live":
        return "실시간 또는 장중 근접 시세 기준입니다. 체결 지연과 호가 변화로 실제 표시값과 차이가 날 수 있습니다."
    if price_status == "mock":
        return "현재 가격과 차트는 mock 데이터입니다. 실제 투자 판단용 시세로 사용하면 안 됩니다."
    return "종가 또는 지연 시세 기준입니다. 장중 체결가와는 차이가 있을 수 있습니다."


def confidence_label(score: float) -> str:
    if score >= 0.82:
        return "높음"
    if score >= 0.68:
        return "보통"
    return "탐색"


def importance_label(score: float) -> str:
    if score >= 0.85:
        return "긴급"
    if score >= 0.68:
        return "중요"
    return "관찰"


def theme_card(theme: Theme) -> dict:
    article_count = len(theme.articles)
    momentum = round(min(0.42 + article_count * 0.07 + len(theme.stocks) * 0.03, 0.96), 4)
    lead = max(theme.articles, key=lambda article: article.published_at, default=None)
    return {
        "id": str(theme.id),
        "slug": theme.slug,
        "name": theme.name_ko,
        "description": theme.description_ko,
        "momentumScore": momentum,
        "articleCount": article_count,
        "confidenceLabel": confidence_label(momentum),
        "leadNarrative": lead.title if lead else theme.description_ko,
    }


def _provider_content_mode(provider: str) -> str:
    return "mock" if provider.startswith("mock-") else "live"


def _naver_original_url(url: str) -> str | None:
    parsed = urlparse(url)
    if "finance.naver.com" not in parsed.netloc:
        return None
    query = parse_qs(parsed.query)
    office_id = query.get("office_id", [None])[0]
    article_id = query.get("article_id", [None])[0]
    if office_id and article_id:
        return f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"
    return None


def _link_meta(article: Article) -> dict[str, str | None]:
    extra = article.extra or {}
    source_home_url = extra.get("source_home_url")
    original_url = extra.get("original_url") or _naver_original_url(article.url)
    parsed = urlparse(article.url) if article.url else None
    host = parsed.netloc.lower() if parsed else ""

    if not article.url:
        return {
            "url": source_home_url or "",
            "originalUrl": original_url,
            "sourceHomeUrl": source_home_url,
            "linkStatus": "missing",
            "linkHost": urlparse(source_home_url).netloc.lower() if source_home_url else None,
        }

    if "example.com" in host:
        return {
            "url": source_home_url or "",
            "originalUrl": None,
            "sourceHomeUrl": source_home_url,
            "linkStatus": "mock",
            "linkHost": None,
        }

    if original_url:
        return {
            "url": original_url,
            "originalUrl": original_url,
            "sourceHomeUrl": source_home_url,
            "linkStatus": "direct",
            "linkHost": urlparse(original_url).netloc.lower() or host,
        }

    if "news.google.com" in host:
        return {
            "url": article.url,
            "originalUrl": None,
            "sourceHomeUrl": source_home_url,
            "linkStatus": "google-news",
            "linkHost": source_home_url and urlparse(source_home_url).netloc.lower() or host,
        }

    return {
        "url": article.url,
        "originalUrl": article.url,
        "sourceHomeUrl": source_home_url,
        "linkStatus": "direct",
        "linkHost": host or None,
    }


def news_card(article: Article) -> dict:
    ordered_links = sorted(
        article.stock_links,
        key=lambda item: (item.relevance_score, item.upside_score),
        reverse=True,
    )
    link_meta = _link_meta(article)
    return {
        "id": str(article.id),
        "title": article.title,
        "sourceName": article.source_name,
        "sourceType": article.source_type.value,
        "publishedAt": serialize_datetime(article.published_at),
        "summary": article.summary,
        "translatedSummaryKo": article.translated_summary_ko,
        "themes": [theme.name_ko for theme in article.themes],
        "relevanceScore": round(article.relevance_score, 4),
        "sentimentScore": round(article.sentiment_score, 4),
        "importanceLabel": importance_label(article.relevance_score),
        "url": link_meta["url"] or "",
        "originalUrl": link_meta["originalUrl"],
        "sourceHomeUrl": link_meta["sourceHomeUrl"],
        "linkStatus": link_meta["linkStatus"],
        "linkHost": link_meta["linkHost"],
        "contentMode": _provider_content_mode(article.provider),
        "linkedStocks": [{"ticker": link.stock.ticker, "nameKo": link.stock.name_ko} for link in ordered_links[:3]],
    }


def cluster_card(cluster: ArticleCluster) -> dict:
    theme_names = list(dict.fromkeys(theme.name_ko for article in cluster.articles for theme in article.themes))
    return {
        "id": str(cluster.id),
        "clusterKey": cluster.cluster_key,
        "headline": cluster.headline,
        "summary": cluster.summary,
        "articleCount": cluster.article_count,
        "latestPublishedAt": serialize_datetime(cluster.latest_published_at),
        "themes": theme_names,
    }


def ranking_entry(item: dict, stock_map: dict[str, Stock]) -> dict:
    stock = stock_map[item["ticker"]]
    return {
        "ticker": stock.ticker,
        "nameKo": stock.name_ko,
        "market": stock.market.value,
        "sector": stock.sector,
        "currentPrice": _current_price(stock),
        "dayChangePct": _day_change_pct(stock),
        "relevanceScore": round(item.get("relevance_score", 0.0), 4),
        "upsideScore": round(item.get("upside_score", 0.0), 4),
        "confidence": round(item.get("confidence", 0.0), 4),
        "thesis": item.get("reasons", ["뉴스 연결 강도가 높은 후보 종목입니다."])[0],
        "reasons": item.get("reasons", []),
    }


def forecast_widget(forecast: Forecast | None) -> dict:
    disclaimer = "예측값은 확률 기반 추정치이며, 확정적 투자 조언이나 수익 보장을 의미하지 않습니다."
    if forecast is None:
        now = serialize_datetime(datetime.now(UTC))
        return {
            "generatedAt": now,
            "horizon": "close",
            "upProb": 0.34,
            "flatProb": 0.33,
            "downProb": 0.33,
            "closeBand": {"low": 0, "base": 0, "high": 0},
            "intradayOutlook": [],
            "confidence": 0.32,
            "disclaimer": disclaimer,
        }

    return {
        "generatedAt": serialize_datetime(forecast.generated_at),
        "horizon": forecast.forecast_horizon.value,
        "upProb": round(forecast.direction_up_prob, 4),
        "flatProb": round(forecast.direction_flat_prob, 4),
        "downProb": round(forecast.direction_down_prob, 4),
        "closeBand": {
            "low": round(forecast.predicted_close_low or 0, 2),
            "base": round(forecast.predicted_close_base or 0, 2),
            "high": round(forecast.predicted_close_high or 0, 2),
        },
        "intradayOutlook": forecast.intraday_path,
        "confidence": round(min((forecast.direction_up_prob + forecast.direction_flat_prob) / 1.3, 0.97), 4),
        "disclaimer": disclaimer,
    }


def explanation_card(card: ExplanationCard) -> dict:
    return {
        "title": card.title,
        "summary": card.summary_ko,
        "bullets": card.bullets_ko,
        "riskFlags": card.risk_flags,
        "confidence": round(card.confidence, 4),
    }


def price_series(stock: Stock, timeframe: str | None = None) -> list[dict]:
    grouped = _group_prices_by_timeframe(stock)
    selected_timeframe = timeframe or default_chart_timeframe(stock)
    rows = grouped.get(selected_timeframe, [])
    return [
        {
            "time": serialize_datetime(candle.bucket_at),
            "open": round(candle.open, 2),
            "high": round(candle.high, 2),
            "low": round(candle.low, 2),
            "close": round(candle.close, 2),
            "volume": candle.volume,
        }
        for candle in rows
    ]


def stock_map_from_themes(themes: Iterable[Theme]) -> dict[str, Stock]:
    collected: dict[str, Stock] = {}
    for theme in themes:
        for link in theme.stocks:
            collected[link.stock.ticker] = link.stock
    return collected
