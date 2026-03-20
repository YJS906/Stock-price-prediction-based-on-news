from pathlib import Path
import json

import pandas as pd


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def load_seed_articles() -> pd.DataFrame:
    payload = json.loads((_repo_root() / "packages" / "shared" / "data" / "mock-seed.json").read_text(encoding="utf-8"))
    rows = []
    for item in payload["articles"]:
        rows.append(
            {
                "text": f"{item['title']} {item['summary']} {item.get('translated_summary_ko') or ''}",
                "source_type": item["source_type"],
                "theme_labels": item["themes"],
                "is_stock_relevant": 1,
                "ranking_signal": len(item["related_tickers"]) * 0.12 + (0.2 if item["source_type"] == "foreign" else 0.08),
                "forecast_target": 0.54 + len(item["themes"]) * 0.05,
            }
        )
    rows.extend(
        [
            {
                "text": "연예인 예능 복귀와 주말 방송 편성 논란",
                "source_type": "domestic",
                "theme_labels": [],
                "is_stock_relevant": 0,
                "ranking_signal": 0.01,
                "forecast_target": 0.33,
            },
            {
                "text": "지역 축제 교통 통제와 날씨 정보",
                "source_type": "domestic",
                "theme_labels": [],
                "is_stock_relevant": 0,
                "ranking_signal": 0.01,
                "forecast_target": 0.32,
            },
        ]
    )
    return pd.DataFrame(rows)

