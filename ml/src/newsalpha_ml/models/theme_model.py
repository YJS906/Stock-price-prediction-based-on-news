from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer


class ThemeModel:
    def __init__(self) -> None:
        self.label_binarizer = MultiLabelBinarizer()
        self.pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(max_features=2048, ngram_range=(1, 2))),
                ("clf", OneVsRestClassifier(LogisticRegression(max_iter=400))),
            ]
        )

    def fit(self, X, y):
        encoded = self.label_binarizer.fit_transform(y)
        self.pipeline.fit(X, encoded)
        return self

    def evaluate(self, X, y) -> dict:
        encoded = self.label_binarizer.transform(y)
        score = float(self.pipeline.score(X, encoded))
        return {"subset_accuracy": round(score, 4)}

