import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor


class RankingModel:
    """
    Baseline ranker for the MVP.
    LightGBM can replace this class without changing the pipeline contract.
    """

    def __init__(self) -> None:
        self.model = GradientBoostingRegressor(random_state=7)

    def fit(self, X: pd.DataFrame, y):
        self.model.fit(X, y)
        return self

    def evaluate(self, X: pd.DataFrame, y) -> dict:
        score = float(self.model.score(X, y))
        return {"r2": round(score, 4)}

