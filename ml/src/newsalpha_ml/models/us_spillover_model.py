import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

from newsalpha_ml.features.us_spillover_features import TARGET_COLUMNS


class UsSpilloverModel:
    """
    Baseline US-session to next-day KRX spillover model.
    The current implementation is a mock-friendly multi-output forest that can be
    replaced later by a LightGBM or temporal deep-learning stack.
    """

    def __init__(self) -> None:
        self.model = RandomForestRegressor(n_estimators=80, random_state=11)

    def fit(self, X: pd.DataFrame, y: pd.DataFrame):
        self.model.fit(X, y)
        return self

    def evaluate(self, X: pd.DataFrame, y: pd.DataFrame) -> dict:
        prediction = self.model.predict(X)
        pred_frame = pd.DataFrame(prediction, columns=TARGET_COLUMNS, index=y.index)
        metrics = {
            "r2": round(float(r2_score(y, pred_frame, multioutput="uniform_average")), 4),
        }
        for column in TARGET_COLUMNS:
            metrics[f"mae_{column}"] = round(float(mean_absolute_error(y[column], pred_frame[column])), 4)
        return metrics

    def predict_bands(self, X: pd.DataFrame) -> pd.DataFrame:
        X_values = X.to_numpy()
        estimator_predictions = []
        for estimator in self.model.estimators_:
            estimator_predictions.append(estimator.predict(X_values))

        stacked = np.stack(estimator_predictions, axis=0)
        payload: dict[str, list[float]] = {}
        for index, column in enumerate(TARGET_COLUMNS):
            column_predictions = stacked[:, :, index]
            payload[f"{column}_low"] = np.quantile(column_predictions, 0.1, axis=0).round(4).tolist()
            payload[f"{column}_base"] = np.quantile(column_predictions, 0.5, axis=0).round(4).tolist()
            payload[f"{column}_high"] = np.quantile(column_predictions, 0.9, axis=0).round(4).tolist()
        return pd.DataFrame(payload, index=X.index)
