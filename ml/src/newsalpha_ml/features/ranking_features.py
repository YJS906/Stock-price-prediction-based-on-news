import pandas as pd


def build_ranking_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    feature_frame = pd.DataFrame(
        {
            "text_length": df["text"].str.len(),
            "theme_count": df["theme_labels"].apply(len),
            "is_foreign": (df["source_type"] == "foreign").astype(int),
        }
    )
    target = df["ranking_signal"].astype(float)
    return feature_frame, target

