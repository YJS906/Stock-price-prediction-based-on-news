from datetime import datetime
from typing import Iterable

from app.models import Article, ArticleCluster, ExplanationCard, Forecast, MarketPrice, Stock, Theme


def _latest_candles(stock: Stock) -> tuple[MarketPrice | None, MarketPrice | None]:
    if not stock.prices:
        return None, None
    ordered = sorted(stock.prices, key=lambda item: item.bucket_at)
    latest = ordered[-1]
    previous = ordered[-2] if len(ordered) > 1 else latest
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


def quote_meta(stock: Stock) -> dict:
    latest, _ = _latest_candles(stock)
    extra = latest.extra if latest and latest.extra else {}
    return {
        "priceTimeframe": latest.timeframe if latest else "1h",
        "priceSource": latest.source if latest else "mock-market",
        "priceUpdatedAt": extra.get("updated_at") or (latest.bucket_at.isoformat() if latest else None),
        "bestBid": extra.get("best_bid"),
        "bestAsk": extra.get("best_ask"),
    }


def confidence_label(score: float) -> str:
    if score >= 0.82:
        return "높음"
    if score >= 0.68:
        return "보통"
    return "탐색"


def importance_label(score: float) -> str:
    if score >= 0.85:
        return "핵심"
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


def news_card(article: Article) -> dict:
    return {
        "id": str(article.id),
        "title": article.title,
        "sourceName": article.source_name,
        "sourceType": article.source_type.value,
        "publishedAt": article.published_at.isoformat(),
        "summary": article.summary,
        "translatedSummaryKo": article.translated_summary_ko,
        "themes": [theme.name_ko for theme in article.themes],
        "relevanceScore": round(article.relevance_score, 4),
        "sentimentScore": round(article.sentiment_score, 4),
        "importanceLabel": importance_label(article.relevance_score),
        "url": article.url,
    }


def cluster_card(cluster: ArticleCluster) -> dict:
    theme_names = list(dict.fromkeys(theme.name_ko for article in cluster.articles for theme in article.themes))
    return {
        "id": str(cluster.id),
        "clusterKey": cluster.cluster_key,
        "headline": cluster.headline,
        "summary": cluster.summary,
        "articleCount": cluster.article_count,
        "latestPublishedAt": cluster.latest_published_at.isoformat(),
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
        "thesis": item.get("reasons", ["관련성 기반 수혜 가능성"])[0],
        "reasons": item.get("reasons", []),
    }


def forecast_widget(forecast: Forecast | None) -> dict:
    if forecast is None:
        now = datetime.utcnow().isoformat()
        return {
            "generatedAt": now,
            "horizon": "close",
            "upProb": 0.34,
            "flatProb": 0.33,
            "downProb": 0.33,
            "closeBand": {"low": 0, "base": 0, "high": 0},
            "intradayOutlook": [],
            "confidence": 0.32,
            "disclaimer": "예측은 확률적 추정치이며 확정적 투자 조언이 아닙니다.",
        }

    return {
        "generatedAt": forecast.generated_at.isoformat(),
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
        "disclaimer": "예측은 확률적 추정치이며 확정적 투자 조언이 아닙니다.",
    }


def explanation_card(card: ExplanationCard) -> dict:
    return {
        "title": card.title,
        "summary": card.summary_ko,
        "bullets": card.bullets_ko,
        "riskFlags": card.risk_flags,
        "confidence": round(card.confidence, 4),
    }


def price_series(stock: Stock) -> list[dict]:
    ordered = sorted(stock.prices, key=lambda item: item.bucket_at)
    return [
        {
            "time": candle.bucket_at.isoformat(),
            "open": round(candle.open, 2),
            "high": round(candle.high, 2),
            "low": round(candle.low, 2),
            "close": round(candle.close, 2),
            "volume": candle.volume,
        }
        for candle in ordered
    ]


def stock_map_from_themes(themes: Iterable[Theme]) -> dict[str, Stock]:
    collected: dict[str, Stock] = {}
    for theme in themes:
        for link in theme.stocks:
            collected[link.stock.ticker] = link.stock
    return collected
