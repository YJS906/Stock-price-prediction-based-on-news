from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import RankingScope
from app.models import ArticleCluster, RankingSnapshot, StockThemeLink
from app.services.presenters import cluster_card, news_card, ranking_entry


class ClusterService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_clusters(self):
        statement = (
            select(ArticleCluster)
            .options(selectinload(ArticleCluster.articles))
            .order_by(ArticleCluster.latest_published_at.desc())
        )
        return [cluster_card(cluster) for cluster in self.db.scalars(statement).all()]

    def get_cluster_detail(self, cluster_id: UUID):
        cluster = self.db.scalar(
            select(ArticleCluster).where(ArticleCluster.id == cluster_id).options(selectinload(ArticleCluster.articles))
        )
        if cluster is None:
            return None

        snapshot = self.db.scalar(
            select(RankingSnapshot).where(RankingSnapshot.scope_type == RankingScope.CLUSTER, RankingSnapshot.scope_id == cluster.id)
        )

        stock_map = {}
        for article in cluster.articles:
            for link in article.stock_links:
                stock_map[link.stock.ticker] = link.stock

        return {
            "cluster": cluster_card(cluster),
            "articles": [news_card(article) for article in sorted(cluster.articles, key=lambda item: item.published_at, reverse=True)],
            "ranking": [ranking_entry(item, stock_map) for item in (snapshot.items if snapshot else []) if item["ticker"] in stock_map],
        }

