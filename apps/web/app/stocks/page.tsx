import Link from "next/link";
import { formatPercent, formatWon } from "@newsalpha/shared";

import { SectionHeading } from "@/components/dashboard/section-heading";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getStocks } from "@/lib/api";

function priceStatusLabel(status: string) {
  if (status === "live") return "live";
  if (status === "mock") return "mock";
  return "지연";
}

export default async function StocksPage({
  searchParams
}: {
  searchParams?: { q?: string };
}) {
  const query = searchParams?.q?.trim() ?? "";
  const stocks = await getStocks(query || undefined);

  return (
    <section className="space-y-6">
      <SectionHeading
        eyebrow="Coverage"
        title="종목 검색"
        description="종목명, 종목코드, 일부 별칭까지 고려해 검색합니다. 추천 모델에 아직 연결되지 않은 KRX 종목도 기본 시세와 차트 중심으로 열 수 있습니다."
      />

      <Card>
        <CardContent className="px-6 py-5">
          <form action="/stocks" className="flex flex-col gap-3 lg:flex-row">
            <input
              type="text"
              name="q"
              defaultValue={query}
              placeholder="예: SK하이닉스, 000660, 삼성전자우"
              className="h-12 flex-1 rounded-2xl border border-white/10 bg-white/[0.04] px-4 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan-400/40"
            />
            <button className="h-12 rounded-2xl bg-cyan-400/90 px-5 text-sm font-medium text-slate-950 transition hover:bg-cyan-300">
              검색
            </button>
          </form>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        {stocks.map((stock) => (
          <Link key={stock.ticker} href={`/stocks/${stock.ticker}`}>
            <Card className="h-full transition hover:border-cyan-400/30">
              <CardHeader>
                <div className="flex flex-wrap items-center gap-2">
                  <CardTitle>{stock.nameKo}</CardTitle>
                  {!stock.isTracked ? <Badge variant="warning">미추적 종목</Badge> : null}
                  <Badge variant="info">{priceStatusLabel(stock.priceStatus)}</Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  {stock.ticker} · {stock.market} · {stock.sector}
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-end justify-between gap-4">
                  <div className="text-2xl font-semibold text-white">{formatWon(stock.currentPrice)}</div>
                  <div className={stock.dayChangePct >= 0 ? "text-emerald-300" : "text-rose-300"}>{formatPercent(stock.dayChangePct)}</div>
                </div>
                <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                  {stock.themes.length > 0 ? (
                    stock.themes.map((theme) => (
                      <span key={`${stock.ticker}-${theme}`} className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-white/80">
                        {theme}
                      </span>
                    ))
                  ) : (
                    <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-white/60">
                      테마 연결 준비 중
                    </span>
                  )}
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </section>
  );
}
