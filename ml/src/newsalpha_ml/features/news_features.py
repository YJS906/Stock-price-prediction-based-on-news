import pandas as pd


def build_relevance_frame(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    X = df["text"].fillna("")
    y = df["is_stock_relevant"].astype(int)
    return X, y


def build_theme_frame(df: pd.DataFrame) -> tuple[pd.Series, list[list[str]]]:
    X = df["text"].fillna("")
    y = df["theme_labels"].tolist()
    return X, y

