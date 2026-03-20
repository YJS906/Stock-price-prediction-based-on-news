from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


class RelevanceModel:
    def __init__(self) -> None:
        self.pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(max_features=2048, ngram_range=(1, 2))),
                ("clf", LogisticRegression(max_iter=400)),
            ]
        )

    def fit(self, X, y):
        self.pipeline.fit(X, y)
        return self

    def evaluate(self, X, y) -> dict:
        accuracy = float(self.pipeline.score(X, y))
        return {"accuracy": round(accuracy, 4)}

