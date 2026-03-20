import pandas as pd


def build_forecast_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    feature_frame = pd.DataFrame(
        {
            "theme_count": df["theme_labels"].apply(len),
            "is_foreign": (df["source_type"] == "foreign").astype(int),
            "text_length": df["text"].str.len(),
        }
    )
    target = df["forecast_target"].astype(float)
    return feature_frame, target

