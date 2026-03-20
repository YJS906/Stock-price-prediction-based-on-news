from sqlalchemy.orm import Session

from app.repositories.stock import StockRepository
from app.services.presenters import (
    _current_price,
    _day_change_pct,
    _previous_close,
    available_chart_timeframes,
    default_chart_timeframe,
    explanation_card,
    forecast_widget,
    price_series,
    quote_meta,
)


class StockService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = StockRepository(db)

    def list_stocks(self, query: str | None = None):
        stocks = self.repo.list_stocks(query=query)
        return [
            {
                "ticker": stock.ticker,
                "nameKo": stock.name_ko,
                "market": stock.market.value,
                "sector": stock.sector,
                "currentPrice": _current_price(stock),
                "dayChangePct": _day_change_pct(stock),
                "themes": [link.theme.name_ko for link in stock.themes],
            }
            for stock in stocks
        ]

    def get_stock_detail(self, ticker: str):
        stock = self.repo.get_by_ticker(ticker)
        if stock is None:
            return None

        ordered_forecasts = sorted(stock.forecasts, key=lambda item: item.generated_at, reverse=True)
        forecast = ordered_forecasts[0] if ordered_forecasts else None
        explanations = sorted(stock.explanations, key=lambda item: item.generated_at, reverse=True)[:4]
        ordered_links = sorted(stock.news_links, key=lambda item: item.article.published_at, reverse=True)
        series = price_series(stock)
        meta = quote_meta(stock)

        current_price = _current_price(stock)
        previous_close = _previous_close(stock)
        chart_timeframes = available_chart_timeframes(stock)
        default_timeframe = default_chart_timeframe(stock)

        return {
            "ticker": stock.ticker,
            "nameKo": stock.name_ko,
            "nameEn": stock.name_en,
            "market": stock.market.value,
            "sector": stock.sector,
            "industry": stock.industry,
            "description": stock.description,
            "currentPrice": current_price,
            "previousClose": previous_close,
            "dayChangePct": _day_change_pct(stock),
            "themeNames": [link.theme.name_ko for link in stock.themes],
            "rankingReasons": [reason for card in explanations for reason in card.bullets_ko[:1]][:4],
            "forecast": forecast_widget(forecast),
            "explanationCards": [explanation_card(card) for card in explanations],
            "priceTimeframe": meta["priceTimeframe"],
            "priceSource": meta["priceSource"],
            "priceUpdatedAt": meta["priceUpdatedAt"],
            "chartTimeframes": chart_timeframes,
            "defaultChartTimeframe": default_timeframe,
            "bestBid": meta["bestBid"],
            "bestAsk": meta["bestAsk"],
            "timeline": [
                {
                    "id": str(link.article.id),
                    "title": link.article.title,
                    "publishedAt": link.article.published_at.isoformat(),
                    "themeNames": [theme.name_ko for theme in link.article.themes],
                    "impactDirection": link.impact_direction.value,
                }
                for link in ordered_links[:8]
            ],
            "priceSeries": price_series(stock, default_timeframe) or series,
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
            return None
        ordered_links = sorted(stock.news_links, key=lambda item: item.article.published_at, reverse=True)
        return [
            {
                "id": str(link.article.id),
                "title": link.article.title,
                "publishedAt": link.article.published_at.isoformat(),
                "themeNames": [theme.name_ko for theme in link.article.themes],
                "impactDirection": link.impact_direction.value,
            }
            for link in ordered_links
        ]

    def get_stock_chart(self, ticker: str, timeframe: str):
        stock = self.repo.get_by_ticker(ticker)
        if stock is None:
            return None

        meta = quote_meta(stock)
        chart_timeframes = available_chart_timeframes(stock)
        selected = timeframe if timeframe in chart_timeframes else default_chart_timeframe(stock)
        source_row = next((row for row in stock.prices if row.timeframe == selected), None)

        return {
            "ticker": stock.ticker,
            "timeframe": selected,
            "source": source_row.source if source_row else meta["priceSource"],
            "updatedAt": meta["priceUpdatedAt"],
            "availableTimeframes": chart_timeframes,
            "points": price_series(stock, selected),
        }
