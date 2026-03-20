from sqlalchemy import select

from app.models import Article, Forecast, ForeignNewsImpact, MarketPrice, RankingSnapshot, StockNewsLink


def test_seed_pipeline_persists_entities(db_session):
    assert db_session.scalar(select(Article).limit(1)) is not None
    assert db_session.scalar(select(StockNewsLink).limit(1)) is not None
    assert db_session.scalar(select(ForeignNewsImpact).limit(1)) is not None
    assert db_session.scalar(select(RankingSnapshot).limit(1)) is not None
    assert db_session.scalar(select(Forecast).limit(1)) is not None
    assert db_session.scalar(select(MarketPrice).where(MarketPrice.timeframe == "1m").limit(1)) is not None
    assert db_session.scalar(select(MarketPrice).where(MarketPrice.timeframe == "1d").limit(1)) is not None
    assert db_session.scalar(select(MarketPrice).where(MarketPrice.timeframe == "1w").limit(1)) is not None
    assert db_session.scalar(select(MarketPrice).where(MarketPrice.timeframe == "1mo").limit(1)) is not None


def test_all_seed_articles_are_stock_relevant(db_session):
    articles = db_session.scalars(select(Article)).all()
    assert len(articles) >= 6
    assert all(article.is_stock_relevant for article in articles)
