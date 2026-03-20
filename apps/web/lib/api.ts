import {
  type ArticleDetailResponse,
  type DashboardResponse,
  type LiveNewsResponse,
  type ModelEvaluationReport,
  type PipelineStatusResponse,
  type StockChartResponse,
  type StockDetailResponse,
  type StockListItem,
  type ThemeCard,
  type ThemeDetailResponse
} from "@newsalpha/shared";

export const API_BASE_URL =
  process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/api/v1${path}`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${path}`);
  }

  return response.json() as Promise<T>;
}

export function getDashboard() {
  return apiFetch<DashboardResponse>("/dashboard");
}

export function getThemes() {
  return apiFetch<ThemeCard[]>("/themes");
}

export function getTheme(slug: string) {
  return apiFetch<ThemeDetailResponse>(`/themes/${slug}`);
}

export function getArticles(theme?: string) {
  const query = theme ? `?theme=${encodeURIComponent(theme)}` : "";
  return apiFetch<DashboardResponse["latestNews"]>(`/articles${query}`);
}

export function getLiveArticles(theme?: string, limit = 20) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (theme) params.set("theme", theme);
  return apiFetch<LiveNewsResponse>(`/articles/live?${params.toString()}`);
}

export function getArticle(id: string) {
  return apiFetch<ArticleDetailResponse>(`/articles/${id}`);
}

export function getStocks(query?: string) {
  const suffix = query ? `?q=${encodeURIComponent(query)}` : "";
  return apiFetch<StockListItem[]>(`/stocks${suffix}`);
}

export function getStock(ticker: string) {
  return apiFetch<StockDetailResponse>(`/stocks/${ticker}`);
}

export function getStockChart(ticker: string, timeframe: string) {
  return apiFetch<StockChartResponse>(`/stocks/${ticker}/chart?timeframe=${encodeURIComponent(timeframe)}`);
}

export function getPipelineStatus() {
  return apiFetch<PipelineStatusResponse>("/admin/pipeline-status");
}

export function getEvaluations() {
  return apiFetch<ModelEvaluationReport[]>("/admin/evaluations");
}
