import { type MarketSummaryCard } from "@newsalpha/shared";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function MarketSummary({ cards }: { cards: MarketSummaryCard[] }) {
  return (
    <div className="data-grid">
      {cards.map((card) => (
        <Card key={card.label} className="overflow-hidden">
          <CardHeader className="pb-3">
            <p className="text-xs uppercase tracking-[0.28em] text-muted-foreground">{card.label}</p>
            <CardTitle className="text-3xl">{card.value}</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">{card.change ?? "실시간 상태 지표"}</span>
            <span
              className={
                card.tone === "positive"
                  ? "text-emerald-300"
                  : card.tone === "negative"
                    ? "text-rose-300"
                    : "text-cyan-200"
              }
            >
              {card.tone === "positive" ? "강세" : card.tone === "negative" ? "주의" : "중립"}
            </span>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
