export type NewsSourceType = "domestic" | "foreign";
export type ImpactDirection = "positive" | "neutral" | "negative" | "mixed";
export type MarketRegime = "bullish" | "neutral" | "risk-off";

export interface MarketSummaryCard {
  label: string;
  value: string;
  change?: string;
  tone: "positive" | "neutral" | "negative";
}

export interface ThemeCard {
  id: string;
  slug: string;
  name: string;
  description: string;
  momentumScore: number;
  articleCount: number;
  confidenceLabel: string;
  leadNarrative: string;
}

export interface NewsCard {
  id: string;
  title: string;
  sourceName: string;
  sourceType: NewsSourceType;
  publishedAt: string;
  summary: string;
  translatedSummaryKo?: string | null;
  themes: string[];
  relevanceScore: number;
  sentimentScore: number;
  importanceLabel: string;
  url: string;
}

export interface RankingEntry {
  ticker: string;
  nameKo: string;
  market: string;
  sector: string;
  currentPrice: number;
  dayChangePct: number;
  relevanceScore: number;
  upsideScore: number;
  confidence: number;
  thesis: string;
  reasons: string[];
}

export interface ArticleClusterCard {
  id: string;
  clusterKey: string;
  headline: string;
  summary: string;
  articleCount: number;
  latestPublishedAt: string;
  themes: string[];
}

export interface DashboardResponse {
  generatedAt: string;
  marketSummary: MarketSummaryCard[];
  topThemes: ThemeCard[];
  latestNews: NewsCard[];
  featuredRanking: RankingEntry[];
  hotClusters: ArticleClusterCard[];
}

export interface ThemeDetailResponse {
  theme: ThemeCard;
  clusters: ArticleClusterCard[];
  articles: NewsCard[];
  ranking: RankingEntry[];
}

export interface ForeignImpactPanel {
  translatedSummaryKo: string;
  koreaImpactSummary: string;
  affectedThemes: string[];
  affectedStocks: string[];
  confidence: number;
}

export interface ArticleDetailResponse {
  id: string;
  title: string;
  sourceName: string;
  sourceType: NewsSourceType;
  publishedAt: string;
  language: string;
  summary: string;
  body?: string | null;
  translatedSummaryKo?: string | null;
  url: string;
  themes: ThemeCard[];
  linkedStocks: RankingEntry[];
  cluster?: ArticleClusterCard | null;
  foreignImpact?: ForeignImpactPanel | null;
}

export interface ForecastBand {
  low: number;
  base: number;
  high: number;
}

export interface IntradayOutlookPoint {
  label: string;
  bullish: number;
  neutral: number;
  bearish: number;
}

export interface ForecastWidget {
  generatedAt: string;
  horizon: string;
  upProb: number;
  flatProb: number;
  downProb: number;
  closeBand: ForecastBand;
  intradayOutlook: IntradayOutlookPoint[];
  confidence: number;
  disclaimer: string;
}

export interface ExplanationCard {
  title: string;
  summary: string;
  bullets: string[];
  riskFlags: string[];
  confidence: number;
}

export interface TimelineItem {
  id: string;
  title: string;
  publishedAt: string;
  themeNames: string[];
  impactDirection: ImpactDirection;
}

export interface PricePoint {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface StockDetailResponse {
  ticker: string;
  nameKo: string;
  nameEn?: string | null;
  market: string;
  sector: string;
  industry: string;
  description: string;
  currentPrice: number;
  previousClose: number;
  dayChangePct: number;
  themeNames: string[];
  rankingReasons: string[];
  forecast: ForecastWidget;
  explanationCards: ExplanationCard[];
  priceTimeframe: string;
  priceSource: string;
  priceUpdatedAt?: string | null;
  bestBid?: number | null;
  bestAsk?: number | null;
  timeline: TimelineItem[];
  priceSeries: PricePoint[];
}

export interface PipelineStatusResponse {
  lastIngestedAt: string;
  articlesSeen: number;
  articlesStored: number;
  stockRelevantRate: number;
  queueDepth: number;
  workerStatus: string;
  providers: Array<{
    name: string;
    kind: NewsSourceType;
    status: string;
    lastFetchedAt: string;
  }>;
}

export interface ModelEvaluationReport {
  modelName: string;
  version: string;
  updatedAt: string;
  summary: string;
  metrics: Array<{
    label: string;
    value: string;
    note: string;
  }>;
}
