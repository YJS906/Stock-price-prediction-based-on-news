import pandas as pd
from sklearn.ensemble import RandomForestRegressor


class ForecastModel:
    """
    Baseline short-horizon model.
    A temporal PyTorch model can replace this implementation later.
    """

    def __init__(self) -> None:
        self.model = RandomForestRegressor(n_estimators=50, random_state=7)

    def fit(self, X: pd.DataFrame, y):
        self.model.fit(X, y)
        return self

    def evaluate(self, X: pd.DataFrame, y) -> dict:
        score = float(self.model.score(X, y))
        return {"r2": round(score, 4)}

