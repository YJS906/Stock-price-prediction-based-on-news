from dataclasses import dataclass


@dataclass(slots=True)
class RelevanceResult:
    is_stock_relevant: bool
    relevance_score: float
    sentiment_score: float


class StockRelevanceClassifier:
    positive_keywords = {
        "hbm",
        "ai",
        "반도체",
        "수주",
        "투자",
        "변압기",
        "원전",
        "방산",
        "배터리",
        "cdmo",
        "로봇",
        "데이터센터",
        "ess",
        "defense",
        "munitions",
        "artillery",
        "grid",
        "storage",
        "biotech",
        "manufacturing",
        "hyperscaler",
        "nvidia",
        "semiconductor",
        "chip",
        "주가",
        "증시",
        "실적",
        "코스피",
        "코스닥",
        "목표가",
        "외국인",
        "기관",
        "매수",
        "매도",
        "테마",
        "지상무기",
        "무기",
        "생산능력",
    }
    negative_keywords = {"연예", "사건", "범죄", "부고", "가십", "스캔들", "예능"}

    def evaluate(self, title: str, summary: str) -> RelevanceResult:
        text = f"{title} {summary}".lower()
        positive_hits = sum(keyword in text for keyword in self.positive_keywords)
        negative_hits = sum(keyword in text for keyword in self.negative_keywords)

        score = min(0.25 + positive_hits * 0.12, 0.97) - negative_hits * 0.15
        score = max(min(score, 0.99), 0.01)
        is_relevant = score >= 0.45 and positive_hits > negative_hits

        sentiment = 0.15
        if any(token in text for token in {"expand", "확대", "증설", "accelerate", "조기", "rebound", "boosting"}):
            sentiment += 0.28
        if any(token in text for token in {"tighten", "risk", "delay", "둔화"}):
            sentiment -= 0.18

        return RelevanceResult(
            is_stock_relevant=is_relevant,
            relevance_score=round(score, 4),
            sentiment_score=round(max(min(sentiment, 0.95), -0.95), 4),
        )
