import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Table, Text, UniqueConstraint, func
from sqlalchemy import Uuid as SqlUuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import (
    ClusterStatus,
    ForecastHorizon,
    ImpactDirection,
    MarketCode,
    MarketScope,
    RankingScope,
    SourceType,
)
from app.db.base import Base

VECTOR_TYPE = JSON().with_variant(Vector(384), "postgresql")


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Theme(TimestampMixin, Base):
    __tablename__ = "themes"

    id: Mapped[uuid.UUID] = mapped_column(SqlUuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name_ko: Mapped[str] = mapped_column(String(120), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(120))
    description_ko: Mapped[str] = mapped_column(Text, nullable=False)
    description_en: Mapped[str | None] = mapped_column(Text)
    market_regime: Mapped[str] = mapped_column(String(32), default="neutral")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)

    stocks: Mapped[list["StockThemeLink"]] = relationship(back_populates="theme", cascade="all, delete-orphan")
    articles: Mapped[list["Article"]] = relationship(secondary="article_theme_links", back_populates="themes")


class Stock(TimestampMixin, Base):
    __tablename__ = "stocks"

    id: Mapped[uuid.UUID] = mapped_column(SqlUuid, primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name_ko: Mapped[str] = mapped_column(String(120), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(120))
    market: Mapped[MarketCode] = mapped_column(Enum(MarketCode), nullable=False)
    sector: Mapped[str] = mapped_column(String(120), nullable=False)
    industry: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[str] = mapped_column(String(8), default="KR")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)

    themes: Mapped[list["StockThemeLink"]] = relationship(back_populates="stock", cascade="all, delete-orphan")
    news_links: Mapped[list["StockNewsLink"]] = relationship(back_populates="stock", cascade="all, delete-orphan")
    forecasts: Mapped[list["Forecast"]] = relationship(back_populates="stock", cascade="all, delete-orphan")
    explanations: Mapped[list["ExplanationCard"]] = relationship(back_populates="stock", cascade="all, delete-orphan")
    prices: Mapped[list["MarketPrice"]] = relationship(back_populates="stock", cascade="all, delete-orphan")


class ArticleCluster(TimestampMixin, Base):
    __tablename__ = "article_clusters"

    id: Mapped[uuid.UUID] = mapped_column(SqlUuid, primary_key=True, default=uuid.uuid4)
    cluster_key: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    headline: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    theme_signal: Mapped[float] = mapped_column(Float, default=0.0)
    article_count: Mapped[int] = mapped_column(Integer, default=0)
    latest_published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ClusterStatus] = mapped_column(Enum(ClusterStatus), default=ClusterStatus.ACTIVE)
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)

    articles: Mapped[list["Article"]] = relationship(secondary="cluster_article_links", back_populates="clusters")
    explanations: Mapped[list["ExplanationCard"]] = relationship(back_populates="cluster")
    forecasts: Mapped[list["Forecast"]] = relationship(back_populates="cluster")


class Article(TimestampMixin, Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(SqlUuid, primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    source_name: Mapped[str] = mapped_column(String(80), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(120), index=True)
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str | None] = mapped_column(Text)
    translated_summary_ko: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    language: Mapped[str] = mapped_column(String(12), nullable=False)
    authors: Mapped[list[str]] = mapped_column(JSON, default=list)
    image_url: Mapped[str | None] = mapped_column(Text)
    symbols_hint: Mapped[list[str]] = mapped_column(JSON, default=list)
    dedupe_hash: Mapped[str] = mapped_column(String(64), index=True)
    is_stock_relevant: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)
    market_scope: Mapped[MarketScope] = mapped_column(Enum(MarketScope), default=MarketScope.KOREA)
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(VECTOR_TYPE)

    themes: Mapped[list["Theme"]] = relationship(secondary="article_theme_links", back_populates="articles")
    clusters: Mapped[list["ArticleCluster"]] = relationship(secondary="cluster_article_links", back_populates="articles")
    stock_links: Mapped[list["StockNewsLink"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    foreign_impact: Mapped["ForeignNewsImpact | None"] = relationship(back_populates="article", uselist=False)
    explanations: Mapped[list["ExplanationCard"]] = relationship(back_populates="article")


class StockThemeLink(TimestampMixin, Base):
    __tablename__ = "stock_theme_links"
    __table_args__ = (UniqueConstraint("stock_id", "theme_id", "relation_type"),)

    id: Mapped[uuid.UUID] = mapped_column(SqlUuid, primary_key=True, default=uuid.uuid4)
    stock_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"))
    theme_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("themes.id", ondelete="CASCADE"))
    relation_type: Mapped[str] = mapped_column(String(80), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    supporting_entities: Mapped[list[str]] = mapped_column(JSON, default=list)
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)

    stock: Mapped["Stock"] = relationship(back_populates="themes")
    theme: Mapped["Theme"] = relationship(back_populates="stocks")


class StockNewsLink(TimestampMixin, Base):
    __tablename__ = "stock_news_links"
    __table_args__ = (UniqueConstraint("article_id", "stock_id"),)

    id: Mapped[uuid.UUID] = mapped_column(SqlUuid, primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"))
    stock_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"))
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("article_clusters.id", ondelete="SET NULL"))
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    upside_score: Mapped[float] = mapped_column(Float, default=0.0)
    impact_direction: Mapped[ImpactDirection] = mapped_column(Enum(ImpactDirection), default=ImpactDirection.NEUTRAL)
    reasons: Mapped[list[str]] = mapped_column(JSON, default=list)
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)

    article: Mapped["Article"] = relationship(back_populates="stock_links")
    stock: Mapped["Stock"] = relationship(back_populates="news_links")


class Forecast(TimestampMixin, Base):
    __tablename__ = "forecasts"

    id: Mapped[uuid.UUID] = mapped_column(SqlUuid, primary_key=True, default=uuid.uuid4)
    stock_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"))
    theme_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("themes.id", ondelete="SET NULL"))
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("article_clusters.id", ondelete="SET NULL"))
    forecast_horizon: Mapped[ForecastHorizon] = mapped_column(Enum(ForecastHorizon), nullable=False)
    direction_up_prob: Mapped[float] = mapped_column(Float, default=0.0)
    direction_flat_prob: Mapped[float] = mapped_column(Float, default=0.0)
    direction_down_prob: Mapped[float] = mapped_column(Float, default=0.0)
    predicted_close_low: Mapped[float | None] = mapped_column(Float)
    predicted_close_base: Mapped[float | None] = mapped_column(Float)
    predicted_close_high: Mapped[float | None] = mapped_column(Float)
    intraday_path: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    confidence_interval: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    feature_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    stock: Mapped["Stock"] = relationship(back_populates="forecasts")
    theme: Mapped["Theme | None"] = relationship()
    cluster: Mapped["ArticleCluster | None"] = relationship(back_populates="forecasts")


class RankingSnapshot(Base):
    __tablename__ = "ranking_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(SqlUuid, primary_key=True, default=uuid.uuid4)
    scope_type: Mapped[RankingScope] = mapped_column(Enum(RankingScope), nullable=False)
    scope_id: Mapped[uuid.UUID | None] = mapped_column(SqlUuid)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    ranking_version: Mapped[str] = mapped_column(String(32), default="mvp-v1")
    items: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)


class ExplanationCard(Base):
    __tablename__ = "explanation_cards"

    id: Mapped[uuid.UUID] = mapped_column(SqlUuid, primary_key=True, default=uuid.uuid4)
    stock_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"))
    article_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("articles.id", ondelete="SET NULL"))
    theme_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("themes.id", ondelete="SET NULL"))
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("article_clusters.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    summary_ko: Mapped[str] = mapped_column(Text, nullable=False)
    bullets_ko: Mapped[list[str]] = mapped_column(JSON, default=list)
    evidence: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    risk_flags: Mapped[list[str]] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    stock: Mapped["Stock"] = relationship(back_populates="explanations")
    article: Mapped["Article | None"] = relationship(back_populates="explanations")
    theme: Mapped["Theme | None"] = relationship()
    cluster: Mapped["ArticleCluster | None"] = relationship(back_populates="explanations")


class MarketPrice(Base):
    __tablename__ = "market_prices"
    __table_args__ = (UniqueConstraint("stock_id", "bucket_at", "timeframe"),)

    id: Mapped[uuid.UUID] = mapped_column(SqlUuid, primary_key=True, default=uuid.uuid4)
    stock_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"))
    bucket_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    timeframe: Mapped[str] = mapped_column(String(12), nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(80), default="mock-market")
    extra: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)

    stock: Mapped["Stock"] = relationship(back_populates="prices")


class ForeignNewsImpact(TimestampMixin, Base):
    __tablename__ = "foreign_news_impacts"

    id: Mapped[uuid.UUID] = mapped_column(SqlUuid, primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), unique=True)
    origin_region: Mapped[str] = mapped_column(String(80), nullable=False)
    origin_market: Mapped[str] = mapped_column(String(80), nullable=False)
    translated_summary_ko: Mapped[str] = mapped_column(Text, nullable=False)
    korea_market_impact_summary: Mapped[str] = mapped_column(Text, nullable=False)
    affected_themes: Mapped[list[str]] = mapped_column(JSON, default=list)
    affected_stocks: Mapped[list[str]] = mapped_column(JSON, default=list)
    impact_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    article: Mapped["Article"] = relationship(back_populates="foreign_impact")


article_theme_links = Table(
    "article_theme_links",
    Base.metadata,
    Column("article_id", SqlUuid, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("theme_id", SqlUuid, ForeignKey("themes.id", ondelete="CASCADE"), primary_key=True),
    Column("score", Float, nullable=False, default=0.0),
)

cluster_article_links = Table(
    "cluster_article_links",
    Base.metadata,
    Column("cluster_id", SqlUuid, ForeignKey("article_clusters.id", ondelete="CASCADE"), primary_key=True),
    Column("article_id", SqlUuid, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
)

