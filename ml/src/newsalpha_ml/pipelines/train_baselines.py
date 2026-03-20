from newsalpha_ml.datasets.mock_data import load_seed_articles
from newsalpha_ml.features.forecast_features import build_forecast_frame
from newsalpha_ml.features.news_features import build_relevance_frame, build_theme_frame
from newsalpha_ml.features.ranking_features import build_ranking_frame
from newsalpha_ml.models.forecast_model import ForecastModel
from newsalpha_ml.models.ranking_model import RankingModel
from newsalpha_ml.models.relevance_model import RelevanceModel
from newsalpha_ml.models.theme_model import ThemeModel


def train_all_baselines() -> dict:
    df = load_seed_articles()

    relevance_X, relevance_y = build_relevance_frame(df)
    relevance_model = RelevanceModel().fit(relevance_X, relevance_y)

    theme_X, theme_y = build_theme_frame(df)
    theme_model = ThemeModel().fit(theme_X, theme_y)

    ranking_X, ranking_y = build_ranking_frame(df)
    ranking_model = RankingModel().fit(ranking_X, ranking_y)

    forecast_X, forecast_y = build_forecast_frame(df)
    forecast_model = ForecastModel().fit(forecast_X, forecast_y)

    return {
      "stock-relevance": relevance_model.evaluate(relevance_X, relevance_y),
      "theme-classifier": theme_model.evaluate(theme_X, theme_y),
      "stock-ranking": ranking_model.evaluate(ranking_X, ranking_y),
      "short-horizon-forecast": forecast_model.evaluate(forecast_X, forecast_y),
    }

