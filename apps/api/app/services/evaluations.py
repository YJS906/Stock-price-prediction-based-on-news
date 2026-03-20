import json

from app.core.config import get_settings


class EvaluationService:
    fallback_reports = [
        {
            "modelName": "stock-relevance",
            "version": "baseline-tfidf-logreg",
            "updatedAt": "2026-03-19T09:00:00+09:00",
            "summary": "주식 관련 기사 필터 베이스라인. 연예·사건·생활 잡음을 제거하는 데 초점.",
            "metrics": [
                {"label": "Macro F1", "value": "0.82", "note": "mock holdout"},
                {"label": "Precision", "value": "0.87", "note": "잡음 기사 억제 우선"},
                {"label": "Recall", "value": "0.78", "note": "보수적 필터링"},
            ],
        },
        {
            "modelName": "theme-classifier",
            "version": "baseline-ovr-linear",
            "updatedAt": "2026-03-19T09:00:00+09:00",
            "summary": "멀티라벨 테마 분류 베이스라인. AI 인프라, 방산, 전력망 등 핵심 테마 우선.",
            "metrics": [
                {"label": "Micro F1", "value": "0.79", "note": "multi-label"},
                {"label": "Coverage", "value": "0.91", "note": "상위 6개 테마"},
                {"label": "Calibration", "value": "0.08", "note": "Brier score"},
            ],
        },
        {
            "modelName": "stock-ranking",
            "version": "heuristic-lgbm-ready",
            "updatedAt": "2026-03-19T09:00:00+09:00",
            "summary": "기사-테마-종목 점수화 규칙 기반 MVP. LightGBM 랭커 교체 지점 포함.",
            "metrics": [
                {"label": "Top10 HitRate", "value": "0.61", "note": "mock event reaction"},
                {"label": "NDCG@10", "value": "0.68", "note": "theme ranking"},
                {"label": "Explainability", "value": "High", "note": "규칙 기반 근거 보존"},
            ],
        },
        {
            "modelName": "short-horizon-forecast",
            "version": "probabilistic-heuristic",
            "updatedAt": "2026-03-19T09:00:00+09:00",
            "summary": "단기 방향성과 종가 밴드를 확률적으로 제시하는 MVP용 베이스라인.",
            "metrics": [
                {"label": "Brier", "value": "0.19", "note": "directional"},
                {"label": "Coverage 80%", "value": "0.77", "note": "close band"},
                {"label": "Intraday MAE", "value": "0.84%", "note": "mock walk-forward"},
            ],
        },
    ]

    def list_reports(self):
        path = get_settings().ml_reports_path
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return self.fallback_reports

    def get_report(self, model_name: str):
        reports = self.list_reports()
        for report in reports:
            if report["modelName"] == model_name:
                return report
        return None

