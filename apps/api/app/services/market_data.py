from collections.abc import Iterable
from datetime import UTC, datetime
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup


class NaverMarketDataService:
    korea_tz = ZoneInfo("Asia/Seoul")

    def fetch(self, ticker: str) -> dict | None:
        minute_payload = self._minute_payload(ticker)
        if minute_payload:
            return minute_payload
        return self._daily_payload(ticker)

    def _minute_payload(self, ticker: str) -> dict | None:
        try:
            rows = self._fetch_minute_rows(ticker)
        except Exception:
            return None
        if not rows:
            return None

        latest = rows[-1]
        current_price = latest["close"]
        delta = latest["change"]
        previous_close = current_price - delta if delta is not None else rows[0]["close"]
        best_ask = latest["best_ask"]
        best_bid = latest["best_bid"]

        candles = [
            {
                "bucket_at": row["bucket_at"],
                "timeframe": "1m",
                "open": row["close"],
                "high": row["close"],
                "low": row["close"],
                "close": row["close"],
                "volume": int(row["volume"]),
                "source": "naver-minute",
                "extra": {
                    "best_bid": best_bid,
                    "best_ask": best_ask,
                    "previous_close": previous_close,
                    "session": "live",
                },
            }
            for row in rows
        ]

        return {
            "timeframe": "1m",
            "source": "naver-minute",
            "updated_at": candles[-1]["bucket_at"].isoformat(),
            "current_price": current_price,
            "previous_close": previous_close,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "candles": candles,
        }

    def _daily_payload(self, ticker: str) -> dict | None:
        try:
            import FinanceDataReader as fdr

            end = datetime.now().date().isoformat()
            frame = fdr.DataReader(ticker, "2026-01-01", end)
        except Exception:
            return None
        if frame is None or frame.empty:
            return None

        frame = frame.sort_index().tail(90)
        latest = frame.iloc[-1]
        previous_close = float(frame.iloc[-2]["Close"]) if len(frame) > 1 else float(latest["Close"])
        candles = [
            {
                "bucket_at": self._as_utc(timestamp.to_pydatetime()),
                "timeframe": "1d",
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
                "source": "naver-day",
                "extra": {
                    "previous_close": previous_close,
                    "session": "live",
                },
            }
            for timestamp, row in frame.iterrows()
        ]

        return {
            "timeframe": "1d",
            "source": "naver-day",
            "updated_at": candles[-1]["bucket_at"].isoformat(),
            "current_price": float(latest["Close"]),
            "previous_close": previous_close,
            "best_bid": None,
            "best_ask": None,
            "candles": candles,
        }

    def _parse_signed_number(self, value) -> float | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        sign = -1 if text.startswith("-") else 1
        cleaned = "".join(char for char in text if char.isdigit() or char == ".")
        if not cleaned:
            return None
        return sign * float(cleaned)

    def _as_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=self.korea_tz)
        return value.astimezone(UTC)

    def _fetch_minute_rows(self, ticker: str) -> list[dict]:
        rows: list[dict] = []
        day_anchor = datetime.now(self.korea_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        thistime = datetime.now(self.korea_tz).strftime("%Y%m%d180000")

        with httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
            },
            timeout=10.0,
            follow_redirects=True,
        ) as client:
            for page in range(1, 13):
                params = urlencode({"code": ticker, "thistime": thistime, "page": page})
                response = client.get(f"https://finance.naver.com/item/sise_time.nhn?{params}")
                response.raise_for_status()
                page_rows = self._parse_minute_page(response.text, day_anchor)
                if not page_rows:
                    break
                rows.extend(page_rows)
                if len(rows) >= 120:
                    break

        unique: dict[datetime, dict] = {}
        for row in rows:
            unique[row["bucket_at"]] = row
        return sorted(unique.values(), key=lambda item: item["bucket_at"])[-120:]

    def _parse_minute_page(self, html: str, day_anchor: datetime) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        parsed_rows: list[dict] = []
        for row in soup.select("table.type2 tr"):
            cells = row.find_all("td")
            if len(cells) < 7:
                continue

            time_text = cells[0].get_text(" ", strip=True)
            price = self._parse_signed_number(cells[1].get_text(" ", strip=True))
            change_value = self._parse_signed_number(cells[2].get_text(" ", strip=True))
            best_ask = self._parse_signed_number(cells[3].get_text(" ", strip=True))
            best_bid = self._parse_signed_number(cells[4].get_text(" ", strip=True))
            trade_delta = self._parse_signed_number(cells[6].get_text(" ", strip=True))
            if price is None or not time_text:
                continue

            direction_label = cells[2].select_one(".blind")
            signed_change = change_value or 0.0
            if direction_label and "하락" in direction_label.get_text(" ", strip=True):
                signed_change *= -1

            hour, minute = [int(token) for token in time_text.split(":", 1)]
            bucket_at = day_anchor.replace(hour=hour, minute=minute)
            parsed_rows.append(
                {
                    "bucket_at": self._as_utc(bucket_at),
                    "close": float(price),
                    "change": float(signed_change),
                    "best_ask": best_ask,
                    "best_bid": best_bid,
                    "volume": int(trade_delta or 0),
                }
            )
        return parsed_rows


def candle_rows_for_storage(payload: dict) -> Iterable[dict]:
    return payload.get("candles", [])
