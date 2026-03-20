from app.models import Article, Theme


class ExplanationEngine:
    def build_article_summary(self, stock_name: str, article: Article, themes: list[Theme], reasons: list[str]) -> dict:
        theme_names = ", ".join(theme.name_ko for theme in themes[:2]) if themes else "관련 테마"
        return {
            "title": f"{stock_name} 연결 근거",
            "summary": f"이 기사는 {theme_names} 흐름에서 {stock_name}의 단기 수혜 가능성을 높이는 신호로 해석됩니다.",
            "bullets": reasons
            + [
                f"기사 중요도 점수 {article.relevance_score:.2f} / 감성 점수 {article.sentiment_score:.2f}",
                "해당 예측은 확률 기반 보조 정보이며 확정적 투자 조언이 아닙니다.",
            ],
            "risk_flags": [
                "실제 수주·실적 반영 시점은 기사 해석보다 느릴 수 있습니다.",
                "동일 테마 내 과열 구간에서는 단기 변동성이 확대될 수 있습니다.",
            ],
            "confidence": round(min((article.relevance_score + max(article.sentiment_score, 0.1)) / 1.6, 0.94), 4),
        }

