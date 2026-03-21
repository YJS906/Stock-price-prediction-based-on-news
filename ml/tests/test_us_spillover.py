from newsalpha_ml.datasets.us_spillover_data import load_mock_us_spillover_pairs
from newsalpha_ml.features.us_spillover_features import TARGET_COLUMNS, build_us_spillover_frame
from newsalpha_ml.models.us_spillover_model import UsSpilloverModel


def test_us_spillover_frame_contains_numeric_and_one_hot_columns():
    df = load_mock_us_spillover_pairs()
    X, y = build_us_spillover_frame(df)

    assert "us_close_return_pct" in X.columns
    assert any(column.startswith("theme_") for column in X.columns)
    assert any(column.startswith("event_") for column in X.columns)
    assert list(y.columns) == TARGET_COLUMNS


def test_us_spillover_model_returns_band_columns():
    df = load_mock_us_spillover_pairs()
    X, y = build_us_spillover_frame(df)
    model = UsSpilloverModel().fit(X, y)
    bands = model.predict_bands(X.head(2))

    assert len(bands) == 2
    assert "kr_next_close_reaction_pct_base" in bands.columns
    assert "kr_next_low_reaction_pct_low" in bands.columns
