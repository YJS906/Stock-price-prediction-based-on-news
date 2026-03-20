import {
  type ArticleDetailResponse,
  type DashboardResponse,
  type ModelEvaluationReport,
  type PipelineStatusResponse,
  type StockDetailResponse,
  type ThemeCard,
  type ThemeDetailResponse
} from "@newsalpha/shared";

const API_BASE_URL =
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

export function getArticles() {
  return apiFetch<DashboardResponse["latestNews"]>("/articles");
}

export function getArticle(id: string) {
  return apiFetch<ArticleDetailResponse>(`/articles/${id}`);
}

export function getStock(ticker: string) {
  return apiFetch<StockDetailResponse>(`/stocks/${ticker}`);
}

export function getPipelineStatus() {
  return apiFetch<PipelineStatusResponse>("/admin/pipeline-status");
}

export function getEvaluations() {
  return apiFetch<ModelEvaluationReport[]>("/admin/evaluations");
}
