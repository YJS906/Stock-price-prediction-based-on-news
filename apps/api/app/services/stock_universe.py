from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import Lock
from typing import Any

_CACHE_TTL = timedelta(hours=6)
_cache_lock = Lock()
_cache_rows: list[dict[str, Any]] = []
_cache_expires_at: datetime | None = None


def normalize_search_text(value: str) -> str:
    return "".join(char for char in value.lower() if char.isalnum())


def _clean_text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    if not text or text.lower() == "nan":
        return fallback
    return text


def _clean_number(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number != number:
        return 0.0
    return number


@dataclass(slots=True)
class UniverseStock:
    ticker: str
    name_ko: str
    market: str
    sector: str
    industry: str
    current_price: float
    day_change_pct: float


class KrStockUniverseService:
    def search(self, query: str, limit: int = 25) -> list[UniverseStock]:
        normalized_query = normalize_search_text(query)
        if not normalized_query:
            return []

        matches: list[tuple[int, UniverseStock]] = []
        for row in self._rows():
            ticker = _clean_text(row.get("Code"))
            name = _clean_text(row.get("Name"))
            market = _clean_text(row.get("Market"), "KOSPI")
            sector = _clean_text(row.get("Dept") or row.get("Sector"), market)
            industry = _clean_text(row.get("Industry"), sector)
            close = _clean_number(row.get("Close"))
            change_pct = _clean_number(row.get("ChagesRatio") or row.get("ChangesRatio"))

            score = self._match_score(normalized_query, ticker=ticker, name=name)
            if score <= 0:
                continue

            matches.append(
                (
                    score,
                    UniverseStock(
                        ticker=ticker,
                        name_ko=name,
                        market=market,
                        sector=sector,
                        industry=industry,
                        current_price=round(close, 2),
                        day_change_pct=round(change_pct, 2),
                    ),
                )
            )

        matches.sort(key=lambda item: (-item[0], item[1].name_ko))
        return [stock for _, stock in matches[:limit]]

    def get_by_ticker(self, ticker: str) -> UniverseStock | None:
        for row in self._rows():
            if _clean_text(row.get("Code")) == ticker:
                market = _clean_text(row.get("Market"), "KOSPI")
                sector = _clean_text(row.get("Dept") or row.get("Sector"), market)
                industry = _clean_text(row.get("Industry"), sector)
                return UniverseStock(
                    ticker=ticker,
                    name_ko=_clean_text(row.get("Name"), ticker),
                    market=market,
                    sector=sector,
                    industry=industry,
                    current_price=round(_clean_number(row.get("Close")), 2),
                    day_change_pct=round(_clean_number(row.get("ChagesRatio") or row.get("ChangesRatio")), 2),
                )
        return None

    def _match_score(self, normalized_query: str, ticker: str, name: str) -> int:
        normalized_name = normalize_search_text(name)
        normalized_ticker = normalize_search_text(ticker)
        if normalized_query == normalized_ticker:
            return 120
        if normalized_query == normalized_name:
            return 110
        if normalized_ticker.startswith(normalized_query):
            return 100
        if normalized_name.startswith(normalized_query):
            return 95
        if normalized_query in normalized_name:
            return 85
        if normalized_query in normalized_ticker:
            return 80
        return 0

    def _rows(self) -> list[dict[str, Any]]:
        global _cache_rows, _cache_expires_at

        now = datetime.now(UTC)
        if _cache_expires_at and now < _cache_expires_at and _cache_rows:
            return _cache_rows

        with _cache_lock:
            now = datetime.now(UTC)
            if _cache_expires_at and now < _cache_expires_at and _cache_rows:
                return _cache_rows

            try:
                import FinanceDataReader as fdr

                frame = fdr.StockListing("KRX")
                rows = frame.to_dict("records")
            except Exception:
                rows = _cache_rows

            _cache_rows = rows
            _cache_expires_at = now + _CACHE_TTL
            return _cache_rows
