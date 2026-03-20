from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories.stock import StockRepository
from app.services.market_data import NaverMarketDataService
from app.services.presenters import (
    _current_price,
    _day_change_pct,
    _previous_close,
    available_chart_timeframes,
    default_chart_timeframe,
    explanation_card,
    forecast_widget,
    price_disclaimer,
    price_series,
    price_status_from_source,
    quote_meta,
    serialize_datetime,
)
from app.services.stock_universe import KrStockUniverseService, UniverseStock, normalize_search_text


class StockService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = StockRepository(db)
        self.settings = get_settings()
        self.market_data = NaverMarketDataService()
        self.universe = KrStockUniverseService()

    def list_stocks(self, query: str | None = None):
        normalized_query = normalize_search_text(query or "")
        tracked_stocks = self.repo.list_stocks(limit=300)

        tracked_results: list[tuple[int, dict[str, Any]]] = []
        for stock in tracked_stocks:
            match_score, match_type = self._tracked_match(stock, normalized_query)
            if normalized_query and match_score <= 0:
                continue

            meta = quote_meta(stock)
            tracked_results.append(
                (
                    match_score or 70,
                    {
                        "ticker": stock.ticker,
                        "nameKo": stock.name_ko,
                        "market": stock.market.value,
                        "sector": stock.sector,
                        "currentPrice": _current_price(stock),
                        "dayChangePct": _day_change_pct(stock),
                        "themes": [link.theme.name_ko for link in stock.themes],
                        "isTracked": True,
                        "priceSource": meta["priceSource"],
                        "priceStatus": meta["priceStatus"],
                        "priceUpdatedAt": meta["priceUpdatedAt"],
                        "matchType": match_type,
                    },
                )
            )

        tracked_results.sort(key=lambda item: (-item[0], item[1]["nameKo"]))
        merged: list[dict[str, Any]] = []
        seen = set()

        for _, item in tracked_results:
            merged.append(item)
            seen.add(item["ticker"])

        if normalized_query:
            for stock in self.universe.search(query or "", limit=80):
                if stock.ticker in seen:
                    continue
                merged.append(self._universe_stock_list_item(stock, match_type="krx-universe"))
                seen.add(stock.ticker)

        return merged[:25]

    def get_stock_detail(self, ticker: str):
        stock = self.repo.get_by_ticker(ticker)
        live_bundle = self._live_market_bundle(ticker)

        if stock is None:
            universe_stock = self.universe.get_by_ticker(ticker)
            if universe_stock is None:
                return None
            return self._untracked_stock_detail(universe_stock, live_bundle)

        ordered_forecasts = sorted(stock.forecasts, key=lambda item: item.generated_at, reverse=True)
        forecast = forecast_widget(ordered_forecasts[0] if ordered_forecasts else None)
        explanations = sorted(stock.explanations, key=lambda item: item.generated_at, reverse=True)[:4]
        ordered_links = sorted(stock.news_links, key=lambda item: item.article.published_at, reverse=True)

        market_snapshot = self._market_snapshot_from_stock(stock, live_bundle=live_bundle)

        return {
            "ticker": stock.ticker,
            "nameKo": stock.name_ko,
            "nameEn": stock.name_en,
            "market": stock.market.value,
            "sector": stock.sector,
            "industry": stock.industry,
            "description": stock.description,
            "currentPrice": market_snapshot["currentPrice"],
            "previousClose": market_snapshot["previousClose"],
            "dayChangePct": market_snapshot["dayChangePct"],
            "themeNames": [link.theme.name_ko for link in stock.themes],
            "isTracked": True,
            "rankingReasons": [reason for card in explanations for reason in card.bullets_ko[:1]][:4],
            "forecast": forecast,
            "explanationCards": [explanation_card(card) for card in explanations],
            "priceTimeframe": market_snapshot["priceTimeframe"],
            "priceSource": market_snapshot["priceSource"],
            "priceStatus": market_snapshot["priceStatus"],
            "priceDisclaimer": price_disclaimer(market_snapshot["priceStatus"]),
            "priceUpdatedAt": market_snapshot["priceUpdatedAt"],
            "chartTimeframes": market_snapshot["chartTimeframes"],
            "defaultChartTimeframe": market_snapshot["defaultChartTimeframe"],
            "bestBid": market_snapshot["bestBid"],
            "bestAsk": market_snapshot["bestAsk"],
            "timeline": [
                {
                    "id": str(link.article.id),
                    "title": link.article.title,
                    "publishedAt": serialize_datetime(link.article.published_at),
                    "themeNames": [theme.name_ko for theme in link.article.themes],
                    "impactDirection": link.impact_direction.value,
                }
                for link in ordered_links[:8]
            ],
            "priceSeries": market_snapshot["priceSeries"],
        }

    def get_stock_forecast(self, ticker: str):
        stock = self.repo.get_by_ticker(ticker)
        if stock is None:
            return None
        ordered = sorted(stock.forecasts, key=lambda item: item.generated_at, reverse=True)
        return forecast_widget(ordered[0] if ordered else None)

    def get_stock_timeline(self, ticker: str):
        stock = self.repo.get_by_ticker(ticker)
        if stock is None:
            return []
        ordered_links = sorted(stock.news_links, key=lambda item: item.article.published_at, reverse=True)
        return [
            {
                "id": str(link.article.id),
                "title": link.article.title,
                "publishedAt": serialize_datetime(link.article.published_at),
                "themeNames": [theme.name_ko for theme in link.article.themes],
                "impactDirection": link.impact_direction.value,
            }
            for link in ordered_links
        ]

    def get_stock_chart(self, ticker: str, timeframe: str):
        stock = self.repo.get_by_ticker(ticker)
        live_bundle = self._live_market_bundle(ticker)
        if live_bundle:
            return self._chart_response_from_live_bundle(ticker=ticker, timeframe=timeframe, bundle=live_bundle)

        if stock is None:
            universe_stock = self.universe.get_by_ticker(ticker)
            if universe_stock is None:
                return None
            return {
                "ticker": ticker,
                "timeframe": "1d",
                "source": "krx-master",
                "priceStatus": "delayed",
                "updatedAt": None,
                "availableTimeframes": ["1d"],
                "points": [],
            }

        meta = quote_meta(stock)
        chart_timeframes = available_chart_timeframes(stock)
        selected = timeframe if timeframe in chart_timeframes else default_chart_timeframe(stock)
        source_row = next((row for row in stock.prices if row.timeframe == selected), None)

        return {
            "ticker": stock.ticker,
            "timeframe": selected,
            "source": source_row.source if source_row else meta["priceSource"],
            "priceStatus": meta["priceStatus"],
            "updatedAt": meta["priceUpdatedAt"],
            "availableTimeframes": chart_timeframes,
            "points": price_series(stock, selected),
        }

    def _tracked_match(self, stock, normalized_query: str) -> tuple[int, str | None]:
        if not normalized_query:
            return 0, None

        aliases = [str(alias) for alias in stock.extra.get("aliases", [])] if stock.extra else []
        candidates = [
            ("ticker", stock.ticker),
            ("name", stock.name_ko),
            ("name-en", stock.name_en or ""),
            *[("alias", alias) for alias in aliases],
        ]

        best_score = 0
        best_match_type = None
        for match_type, value in candidates:
            normalized_value = normalize_search_text(value or "")
            if not normalized_value:
                continue
            if normalized_query == normalized_value:
                return 120, match_type
            if normalized_value.startswith(normalized_query):
                score = 105 if match_type == "ticker" else 100
            elif normalized_query in normalized_value:
                score = 90 if match_type == "alias" else 85
            else:
                score = 0
            if score > best_score:
                best_score = score
                best_match_type = match_type
        return best_score, best_match_type

    def _universe_stock_list_item(self, stock: UniverseStock, match_type: str) -> dict[str, Any]:
        return {
            "ticker": stock.ticker,
            "nameKo": stock.name_ko,
            "market": stock.market,
            "sector": stock.sector,
            "currentPrice": stock.current_price,
            "dayChangePct": stock.day_change_pct,
            "themes": [],
            "isTracked": False,
            "priceSource": "krx-master",
            "priceStatus": "delayed",
            "priceUpdatedAt": None,
            "matchType": match_type,
        }

    def _live_market_bundle(self, ticker: str) -> dict | None:
        if self.settings.market_data_provider_mode.lower() == "mock":
            return None
        try:
            return self.market_data.fetch(ticker)
        except Exception:
            return None

    def _market_snapshot_from_stock(self, stock, live_bundle: dict | None = None) -> dict[str, Any]:
        if live_bundle:
            return self._market_snapshot_from_bundle(live_bundle)

        meta = quote_meta(stock)
        chart_timeframes = available_chart_timeframes(stock)
        default_timeframe = default_chart_timeframe(stock)
        return {
            "currentPrice": _current_price(stock),
            "previousClose": _previous_close(stock),
            "dayChangePct": _day_change_pct(stock),
            "priceTimeframe": meta["priceTimeframe"],
            "priceSource": meta["priceSource"],
            "priceStatus": meta["priceStatus"],
            "priceUpdatedAt": meta["priceUpdatedAt"],
            "bestBid": meta["bestBid"],
            "bestAsk": meta["bestAsk"],
            "chartTimeframes": chart_timeframes,
            "defaultChartTimeframe": default_timeframe,
            "priceSeries": price_series(stock, default_timeframe),
        }

    def _market_snapshot_from_bundle(self, bundle: dict) -> dict[str, Any]:
        chart_timeframes = [timeframe for timeframe in ("1m", "1d", "1w", "1mo") if bundle.get("series", {}).get(timeframe)]
        default_timeframe = "1d" if "1d" in chart_timeframes else (chart_timeframes[0] if chart_timeframes else "1d")
        current_price = round(float(bundle.get("current_price") or 0.0), 2)
        previous_close = round(float(bundle.get("previous_close") or current_price), 2)
        day_change_pct = 0.0 if previous_close == 0 else round(((current_price - previous_close) / previous_close) * 100, 2)
        source = str(bundle.get("source") or "naver-day")
        return {
            "currentPrice": current_price,
            "previousClose": previous_close,
            "dayChangePct": day_change_pct,
            "priceTimeframe": bundle.get("timeframe") or default_timeframe,
            "priceSource": source,
            "priceStatus": str(bundle.get("price_status") or price_status_from_source(source, "live")),
            "priceUpdatedAt": bundle.get("updated_at"),
            "bestBid": bundle.get("best_bid"),
            "bestAsk": bundle.get("best_ask"),
            "chartTimeframes": chart_timeframes or ["1d"],
            "defaultChartTimeframe": default_timeframe,
            "priceSeries": self._serialize_chart_points(bundle.get("series", {}).get(default_timeframe, [])),
        }

    def _untracked_stock_detail(self, stock: UniverseStock, live_bundle: dict | None):
        market_snapshot = self._market_snapshot_from_bundle(live_bundle) if live_bundle else {
            "currentPrice": stock.current_price,
            "previousClose": self._approx_previous_close(stock.current_price, stock.day_change_pct),
            "dayChangePct": stock.day_change_pct,
            "priceTimeframe": "1d",
            "priceSource": "krx-master",
            "priceStatus": "delayed",
            "priceUpdatedAt": None,
            "bestBid": None,
            "bestAsk": None,
            "chartTimeframes": ["1d"],
            "defaultChartTimeframe": "1d",
            "priceSeries": [],
        }
        forecast = forecast_widget(None)
        forecast["disclaimer"] = f"{forecast['disclaimer']} 현재 이 종목은 추천 모델 추적 universe에 포함되지 않아 예측 카드와 뉴스 연결은 제한됩니다."

        return {
            "ticker": stock.ticker,
            "nameKo": stock.name_ko,
            "nameEn": None,
            "market": stock.market,
            "sector": stock.sector,
            "industry": stock.industry,
            "description": "현재는 KRX 종목 마스터 기반 기본 시세와 차트만 제공합니다. 추천 근거와 뉴스 연결은 추적 universe 확장 시 함께 보강됩니다.",
            "currentPrice": market_snapshot["currentPrice"],
            "previousClose": market_snapshot["previousClose"],
            "dayChangePct": market_snapshot["dayChangePct"],
            "themeNames": [],
            "isTracked": False,
            "rankingReasons": ["아직 추천 랭킹과 설명 카드가 생성되지 않은 종목입니다."],
            "forecast": forecast,
            "explanationCards": [],
            "priceTimeframe": market_snapshot["priceTimeframe"],
            "priceSource": market_snapshot["priceSource"],
            "priceStatus": market_snapshot["priceStatus"],
            "priceDisclaimer": f"{price_disclaimer(market_snapshot['priceStatus'])} 현재 이 종목은 미추적 종목이어서 분석 카드 대신 기본 시세 중심으로 제공합니다.",
            "priceUpdatedAt": market_snapshot["priceUpdatedAt"],
            "chartTimeframes": market_snapshot["chartTimeframes"],
            "defaultChartTimeframe": market_snapshot["defaultChartTimeframe"],
            "bestBid": market_snapshot["bestBid"],
            "bestAsk": market_snapshot["bestAsk"],
            "timeline": [],
            "priceSeries": market_snapshot["priceSeries"],
        }

    def _chart_response_from_live_bundle(self, ticker: str, timeframe: str, bundle: dict) -> dict[str, Any]:
        series = bundle.get("series", {})
        available = [item for item in ("1m", "1d", "1w", "1mo") if series.get(item)]
        if not available:
            return {
                "ticker": ticker,
                "timeframe": "1d",
                "source": str(bundle.get("source") or "naver-day"),
                "priceStatus": str(bundle.get("price_status") or "live"),
                "updatedAt": bundle.get("updated_at"),
                "availableTimeframes": ["1d"],
                "points": [],
            }
        selected = timeframe if timeframe in available else ("1d" if "1d" in available else available[0])
        source_map = {
            "1m": "naver-minute",
            "1d": "naver-day",
            "1w": "naver-week",
            "1mo": "naver-month",
        }
        return {
            "ticker": ticker,
            "timeframe": selected,
            "source": source_map.get(selected, str(bundle.get("source") or "naver-day")),
            "priceStatus": str(bundle.get("price_status") or "live"),
            "updatedAt": bundle.get("updated_at"),
            "availableTimeframes": available,
            "points": self._serialize_chart_points(series.get(selected, [])),
        }

    def _serialize_chart_points(self, rows: list[dict]) -> list[dict]:
        return [
            {
                "time": serialize_datetime(row["bucket_at"]) if not isinstance(row["bucket_at"], str) else row["bucket_at"],
                "open": round(float(row["open"]), 2),
                "high": round(float(row["high"]), 2),
                "low": round(float(row["low"]), 2),
                "close": round(float(row["close"]), 2),
                "volume": int(row["volume"]),
            }
            for row in rows
        ]

    def _approx_previous_close(self, current_price: float, day_change_pct: float) -> float:
        if current_price == 0:
            return 0.0
        ratio = 1 + (day_change_pct / 100)
        if ratio == 0:
            return current_price
        return round(current_price / ratio, 2)
