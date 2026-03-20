from collections import defaultdict
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.enums import ImpactDirection, RankingScope
from app.models import ArticleCluster, RankingSnapshot, Stock, StockNewsLink, Theme


class RankingEngine:
    def score_link(self, sentiment_score: float, relevance_score: float, source_type: str, theme_boost: float) -> tuple[float, str]:
        upside = min(0.25 + relevance_score * 0.45 + max(sentiment_score, 0) * 0.25 + theme_boost, 0.98)
        if source_type == "foreign":
            upside = min(upside + 0.04, 0.99)

        if upside >= 0.75:
            direction = ImpactDirection.POSITIVE.value
        elif upside >= 0.52:
            direction = ImpactDirection.MIXED.value
        else:
            direction = ImpactDirection.NEUTRAL.value

        return round(upside, 4), direction

    def rebuild_snapshots(self, db: Session) -> None:
        db.execute(delete(RankingSnapshot))

        stock_map = {stock.id: stock for stock in db.scalars(select(Stock)).all()}
        theme_map = {theme.id: theme for theme in db.scalars(select(Theme)).all()}
        cluster_map = {cluster.id: cluster for cluster in db.scalars(select(ArticleCluster)).all()}

        theme_buckets: dict = defaultdict(list)
        cluster_buckets: dict = defaultdict(list)
        dashboard_bucket: dict = defaultdict(lambda: {"relevance": 0.0, "upside": 0.0, "reasons": []})

        for link in db.scalars(select(StockNewsLink)).all():
            stock = stock_map[link.stock_id]
            item = {
                "ticker": stock.ticker,
                "name_ko": stock.name_ko,
                "market": stock.market.value,
                "sector": stock.sector,
                "relevance_score": round(link.relevance_score, 4),
                "upside_score": round(link.upside_score, 4),
                "confidence": round(min((link.relevance_score + link.upside_score) / 2, 0.98), 4),
                "reasons": link.reasons[:3],
            }

            for theme_link in stock.themes:
                theme_buckets[theme_link.theme_id].append(item)

            if link.cluster_id:
                cluster_buckets[link.cluster_id].append(item)

            bucket = dashboard_bucket[stock.id]
            bucket["stock"] = stock
            bucket["relevance"] += link.relevance_score
            bucket["upside"] += link.upside_score
            bucket["reasons"].extend(link.reasons[:2])

        for theme_id, items in theme_buckets.items():
            theme = theme_map[theme_id]
            db.add(
                RankingSnapshot(
                    scope_type=RankingScope.THEME,
                    scope_id=theme.id,
                    as_of=datetime.utcnow(),
                    items=self._top_items(items),
                    extra={"theme_slug": theme.slug},
                )
            )

        for cluster_id, items in cluster_buckets.items():
            cluster = cluster_map.get(cluster_id)
            if not cluster:
                continue
            db.add(
                RankingSnapshot(
                    scope_type=RankingScope.CLUSTER,
                    scope_id=cluster.id,
                    as_of=datetime.utcnow(),
                    items=self._top_items(items),
                    extra={"cluster_key": cluster.cluster_key},
                )
            )

        dashboard_items = []
        for bucket in dashboard_bucket.values():
            stock = bucket["stock"]
            relevance = min(bucket["relevance"], 0.99)
            upside = min(bucket["upside"] / max(len(bucket["reasons"]), 1) * 1.4, 0.99)
            dashboard_items.append(
                {
                    "ticker": stock.ticker,
                    "name_ko": stock.name_ko,
                    "market": stock.market.value,
                    "sector": stock.sector,
                    "relevance_score": round(relevance, 4),
                    "upside_score": round(upside, 4),
                    "confidence": round(min((relevance + upside) / 2, 0.98), 4),
                    "reasons": list(dict.fromkeys(bucket["reasons"]))[:3],
                }
            )

        db.add(
            RankingSnapshot(
                scope_type=RankingScope.DASHBOARD,
                scope_id=None,
                as_of=datetime.utcnow(),
                items=self._top_items(dashboard_items),
                extra={"scope": "dashboard"},
            )
        )

    def _top_items(self, items: list[dict]) -> list[dict]:
        deduped: dict[str, dict] = {}
        for item in items:
            key = item["ticker"]
            current = deduped.get(key)
            if not current or item["upside_score"] > current["upside_score"]:
                deduped[key] = item
        return sorted(deduped.values(), key=lambda row: (row["upside_score"], row["relevance_score"]), reverse=True)[:15]
