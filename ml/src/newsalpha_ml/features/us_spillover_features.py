import pandas as pd


TARGET_COLUMNS = [
    "kr_next_open_gap_pct",
    "kr_next_high_reaction_pct",
    "kr_next_close_reaction_pct",
    "kr_next_low_reaction_pct",
]


def build_us_spillover_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    numeric = pd.DataFrame(
        {
            "us_close_return_pct": df["us_close_return_pct"].astype(float),
            "us_after_hours_return_pct": df["us_after_hours_return_pct"].astype(float),
            "us_volume_zscore": df["us_volume_zscore"].astype(float),
            "us_range_pct": df["us_range_pct"].astype(float),
            "article_sentiment": df["article_sentiment"].astype(float),
            "correlation_20d": df["correlation_20d"].astype(float),
            "kr_prev_close_return_pct": df["kr_prev_close_return_pct"].astype(float),
            "is_negative_us_shock": (df["us_close_return_pct"] < 0).astype(int),
            "is_positive_after_hours": (df["us_after_hours_return_pct"] > 0).astype(int),
        }
    )
    categorical = pd.get_dummies(
        df[["theme", "event_type", "us_leader_ticker", "kr_ticker"]],
        prefix=["theme", "event", "us", "kr"],
        dtype=int,
    )
    X = pd.concat([numeric, categorical], axis=1)
    y = df[TARGET_COLUMNS].astype(float).copy()
    return X, y
