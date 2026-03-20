from statistics import mean

from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.api import DashboardResponseSchema
from app.services.presenters import cluster_card, news_card, ranking_entry, stock_map_from_themes, theme_card


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = DashboardRepository(db)

    def get_dashboard(self) -> DashboardResponseSchema:
        themes = self.repo.list_active_themes()
        articles = self.repo.list_latest_articles(limit=10)
        clusters = self.repo.list_hot_clusters(limit=5)
        snapshot = self.repo.get_dashboard_snapshot()
        stock_map = stock_map_from_themes(themes)

        featured_ranking = [ranking_entry(item, stock_map) for item in (snapshot.items if snapshot else []) if item["ticker"] in stock_map]
        avg_move = round(mean([item["dayChangePct"] for item in featured_ranking[:5]]) if featured_ranking else 0.0, 2)
        foreign_articles = sum(article.source_type.value == "foreign" for article in articles)
        relevance_rate = round(sum(article.is_stock_relevant for article in articles) / max(len(articles), 1) * 100, 1)

        market_summary = [
            {"label": "활성 테마", "value": f"{len(themes)}개", "change": None, "tone": "positive"},
            {"label": "해외 뉴스", "value": f"{foreign_articles}건", "change": "미국·글로벌 기사 포함", "tone": "neutral"},
            {
                "label": "상위 종목 평균",
                "value": f"{avg_move:+.1f}%",
                "change": "상위 5개 등락률",
                "tone": "positive" if avg_move >= 0 else "negative",
            },
            {"label": "주식 관련성", "value": f"{relevance_rate:.1f}%", "change": "필터 통과 기사 비중", "tone": "neutral"},
        ]

        return DashboardResponseSchema(
            generatedAt=articles[0].published_at.isoformat() if articles else "",
            marketSummary=market_summary,
            topThemes=[theme_card(theme) for theme in sorted(themes, key=lambda row: len(row.articles), reverse=True)[:6]],
            latestNews=[news_card(article) for article in articles],
            featuredRanking=featured_ranking[:10],
            hotClusters=[cluster_card(cluster) for cluster in clusters],
        )
