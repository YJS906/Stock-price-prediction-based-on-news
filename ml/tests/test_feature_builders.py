from newsalpha_ml.datasets.mock_data import load_seed_articles
from newsalpha_ml.features.forecast_features import build_forecast_frame
from newsalpha_ml.features.news_features import build_relevance_frame, build_theme_frame
from newsalpha_ml.features.ranking_features import build_ranking_frame


def test_relevance_features_shape():
    df = load_seed_articles()
    X, y = build_relevance_frame(df)
    assert len(X) == len(df)
    assert len(y) == len(df)


def test_theme_features_preserve_labels():
    df = load_seed_articles()
    _, labels = build_theme_frame(df)
    assert any(labels)


def test_ranking_and_forecast_frames_have_columns():
    df = load_seed_articles()
    ranking_X, _ = build_ranking_frame(df)
    forecast_X, _ = build_forecast_frame(df)
    assert set(ranking_X.columns) == {"text_length", "theme_count", "is_foreign"}
    assert set(forecast_X.columns) == {"theme_count", "is_foreign", "text_length"}

