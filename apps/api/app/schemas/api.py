from pydantic import BaseModel, ConfigDict


class MarketSummaryCardSchema(BaseModel):
    label: str
    value: str
    change: str | None = None
    tone: str


class ThemeCardSchema(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    momentumScore: float
    articleCount: int
    confidenceLabel: str
    leadNarrative: str


class NewsCardSchema(BaseModel):
    id: str
    title: str
    sourceName: str
    sourceType: str
    publishedAt: str
    summary: str
    translatedSummaryKo: str | None = None
    themes: list[str]
    relevanceScore: float
    sentimentScore: float
    importanceLabel: str
    url: str
    linkedStocks: list[dict]


class RankingEntrySchema(BaseModel):
    ticker: str
    nameKo: str
    market: str
    sector: str
    currentPrice: float
    dayChangePct: float
    relevanceScore: float
    upsideScore: float
    confidence: float
    thesis: str
    reasons: list[str]


class ClusterCardSchema(BaseModel):
    id: str
    clusterKey: str
    headline: str
    summary: str
    articleCount: int
    latestPublishedAt: str
    themes: list[str]


class DashboardResponseSchema(BaseModel):
    generatedAt: str
    marketSummary: list[MarketSummaryCardSchema]
    topThemes: list[ThemeCardSchema]
    latestNews: list[NewsCardSchema]
    featuredRanking: list[RankingEntrySchema]
    hotClusters: list[ClusterCardSchema]


class ThemeDetailResponseSchema(BaseModel):
    theme: ThemeCardSchema
    clusters: list[ClusterCardSchema]
    articles: list[NewsCardSchema]
    ranking: list[RankingEntrySchema]


class ForeignImpactSchema(BaseModel):
    translatedSummaryKo: str
    koreaImpactSummary: str
    affectedThemes: list[str]
    affectedStocks: list[str]
    confidence: float


class ArticleDetailResponseSchema(BaseModel):
    id: str
    title: str
    sourceName: str
    sourceType: str
    publishedAt: str
    language: str
    summary: str
    body: str | None = None
    translatedSummaryKo: str | None = None
    url: str
    themes: list[ThemeCardSchema]
    linkedStocks: list[RankingEntrySchema]
    cluster: ClusterCardSchema | None = None
    foreignImpact: ForeignImpactSchema | None = None


class ForecastWidgetSchema(BaseModel):
    generatedAt: str
    horizon: str
    upProb: float
    flatProb: float
    downProb: float
    closeBand: dict
    intradayOutlook: list[dict]
    confidence: float
    disclaimer: str


class ExplanationCardSchema(BaseModel):
    title: str
    summary: str
    bullets: list[str]
    riskFlags: list[str]
    confidence: float


class TimelineItemSchema(BaseModel):
    id: str
    title: str
    publishedAt: str
    themeNames: list[str]
    impactDirection: str


class PricePointSchema(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockListItemSchema(BaseModel):
    ticker: str
    nameKo: str
    market: str
    sector: str
    currentPrice: float
    dayChangePct: float
    themes: list[str]


class StockChartResponseSchema(BaseModel):
    ticker: str
    timeframe: str
    source: str
    updatedAt: str | None = None
    availableTimeframes: list[str]
    points: list[PricePointSchema]


class StockDetailResponseSchema(BaseModel):
    ticker: str
    nameKo: str
    nameEn: str | None = None
    market: str
    sector: str
    industry: str
    description: str
    currentPrice: float
    previousClose: float
    dayChangePct: float
    themeNames: list[str]
    rankingReasons: list[str]
    forecast: ForecastWidgetSchema
    explanationCards: list[ExplanationCardSchema]
    priceTimeframe: str
    priceSource: str
    priceUpdatedAt: str | None = None
    chartTimeframes: list[str]
    defaultChartTimeframe: str
    bestBid: float | None = None
    bestAsk: float | None = None
    timeline: list[TimelineItemSchema]
    priceSeries: list[PricePointSchema]


class LiveNewsResponseSchema(BaseModel):
    generatedAt: str
    pollingIntervalMs: int
    themeSlug: str | None = None
    items: list[NewsCardSchema]


class PipelineProviderStatusSchema(BaseModel):
    name: str
    kind: str
    status: str
    lastFetchedAt: str


class PipelineStatusResponseSchema(BaseModel):
    lastIngestedAt: str
    articlesSeen: int
    articlesStored: int
    stockRelevantRate: float
    queueDepth: int
    workerStatus: str
    providers: list[PipelineProviderStatusSchema]


class EvaluationMetricSchema(BaseModel):
    label: str
    value: str
    note: str


class ModelEvaluationReportSchema(BaseModel):
    modelName: str
    version: str
    updatedAt: str
    summary: str
    metrics: list[EvaluationMetricSchema]


class MutationResponseSchema(BaseModel):
    status: str
    detail: str
    payload: dict
