from collections import defaultdict

from app.models import Theme
from app.services.pipeline.normalizer import NormalizedArticle


class ThemeClassifier:
    keyword_map = {
        "ai-infrastructure": ["ai", "hbm", "데이터센터", "패키징", "서버"],
        "defense-space": ["방산", "탄약", "유도무기", "artillery", "nato", "defense"],
        "power-grid-nuclear": ["전력망", "hvdc", "변압기", "전력", "원전", "grid"],
        "secondary-battery": ["배터리", "양극재", "ess", "cathode", "storage"],
        "biopharma-cdmo": ["cdmo", "바이오", "manufacturing", "생산"],
        "robotics-smartfactory": ["로봇", "협동로봇", "smart factory", "자동화"],
    }

    def classify(self, article: NormalizedArticle, themes: list[Theme]) -> dict[str, float]:
        scores = defaultdict(float)
        text = f"{article.title} {article.summary} {article.translated_summary_ko or ''}".lower()

        for hinted_slug in article.metadata.get("theme_hints", []):
            scores[hinted_slug] += 0.72

        for slug, keywords in self.keyword_map.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    scores[slug] += 0.14

        active = {theme.slug for theme in themes}
        filtered = {slug: min(score, 0.99) for slug, score in scores.items() if slug in active}
        if not filtered:
            filtered["ai-infrastructure"] = 0.42
        return filtered

