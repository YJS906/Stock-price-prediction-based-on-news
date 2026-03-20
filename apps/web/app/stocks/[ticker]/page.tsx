import { notFound } from "next/navigation";
import { formatPercent, formatWon } from "@newsalpha/shared";

import { ForecastChart } from "@/components/charts/forecast-chart";
import { PriceChart } from "@/components/charts/price-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getStock } from "@/lib/api";

function formatUpdatedAt(value?: string | null) {
  if (!value) return "갱신 시각 없음";
  return new Intl.DateTimeFormat("ko-KR", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function sourceLabel(source: string) {
  if (source === "naver-minute") return "네이버 금융 분봉";
  if (source === "naver-day") return "네이버 금융 일봉";
  return "모의 데이터";
}

export default async function StockDetailPage({ params }: { params: { ticker: string } }) {
  try {
    const stock = await getStock(params.ticker);

    return (
      <div className="space-y-8">
        <Card>
          <CardContent className="grid gap-6 px-6 py-8 lg:grid-cols-[1.3fr_0.9fr] lg:px-8">
            <div className="space-y-4">
              <div className="flex flex-wrap gap-2">
                {stock.themeNames.map((theme) => (
                  <Badge key={`${stock.ticker}-${theme}`} variant="info">
                    {theme}
                  </Badge>
                ))}
              </div>
              <div>
                <h1 className="text-4xl font-semibold text-white">{stock.nameKo}</h1>
                <p className="mt-2 text-sm text-muted-foreground">
                  {stock.ticker} · {stock.market} · {stock.industry}
                </p>
              </div>
              <p className="max-w-3xl text-sm leading-7 text-muted-foreground">{stock.description}</p>
              <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                <Badge variant="info">{sourceLabel(stock.priceSource)}</Badge>
                <span>{stock.priceTimeframe === "1d" ? "일봉 기준" : "장중 체결 기준"}</span>
                <span>마지막 갱신 {formatUpdatedAt(stock.priceUpdatedAt)}</span>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-1">
              <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
                <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">현재가</p>
                <div className="mt-3 text-4xl font-semibold text-white">{formatWon(stock.currentPrice)}</div>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
                <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">전일 대비</p>
                <div className={`mt-3 text-4xl font-semibold ${stock.dayChangePct >= 0 ? "text-emerald-300" : "text-rose-300"}`}>
                  {formatPercent(stock.dayChangePct)}
                </div>
                <p className="mt-2 text-xs text-muted-foreground">기준 종가 {formatWon(stock.previousClose)}</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
                <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">호가 기준</p>
                <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
                  <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-3">
                    <div className="text-xs text-emerald-200/80">매수</div>
                    <div className="mt-2 text-lg font-semibold text-emerald-200">
                      {stock.bestBid ? formatWon(stock.bestBid) : "미제공"}
                    </div>
                  </div>
                  <div className="rounded-2xl border border-rose-400/20 bg-rose-400/10 p-3">
                    <div className="text-xs text-rose-200/80">매도</div>
                    <div className="mt-2 text-lg font-semibold text-rose-200">
                      {stock.bestAsk ? formatWon(stock.bestAsk) : "미제공"}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
          <Card>
            <CardHeader>
              <CardTitle>가격 흐름</CardTitle>
            </CardHeader>
            <CardContent>
              <PriceChart data={stock.priceSeries} timeframe={stock.priceTimeframe} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>단기 방향성 확률</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <ForecastChart forecast={stock.forecast} />
              <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                <div className="text-xs uppercase tracking-[0.24em] text-muted-foreground">예상 종가 밴드</div>
                <div className="mt-3 text-lg font-semibold text-cyan-200">
                  {formatWon(stock.forecast.closeBand.low)} - {formatWon(stock.forecast.closeBand.high)}
                </div>
              </div>
              <p className="rounded-2xl border border-amber-400/20 bg-amber-400/10 p-3 text-sm leading-6 text-amber-100">
                {stock.forecast.disclaimer}
              </p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="thesis">
          <TabsList>
            <TabsTrigger value="thesis">랭킹 근거</TabsTrigger>
            <TabsTrigger value="timeline">관련 뉴스</TabsTrigger>
            <TabsTrigger value="intraday">장중 전망</TabsTrigger>
          </TabsList>

          <TabsContent value="thesis">
            <div className="grid gap-4 lg:grid-cols-2">
              {stock.explanationCards.map((card) => (
                <Card key={`${stock.ticker}-${card.title}`}>
                  <CardHeader>
                    <CardTitle>{card.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm leading-6 text-muted-foreground">{card.summary}</p>
                    <ul className="space-y-2 text-sm text-slate-200">
                      {card.bullets.map((bullet) => (
                        <li key={bullet} className="rounded-2xl border border-white/8 bg-white/[0.03] p-3">
                          {bullet}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="timeline">
            <Card>
              <CardHeader>
                <CardTitle>최근 관련 뉴스 타임라인</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {stock.timeline.map((item) => (
                  <div key={item.id} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                    <div className="flex flex-wrap gap-2">
                      {item.themeNames.map((theme) => (
                        <Badge key={`${item.id}-${theme}`}>{theme}</Badge>
                      ))}
                    </div>
                    <div className="mt-3 text-base font-medium text-white">{item.title}</div>
                    <p className="mt-2 text-sm text-muted-foreground">{formatUpdatedAt(item.publishedAt)}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="intraday">
            <Card>
              <CardHeader>
                <CardTitle>장중 시간 구간별 전망</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 lg:grid-cols-3">
                {stock.forecast.intradayOutlook.map((point) => (
                  <div key={point.label} className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
                    <div className="text-sm text-muted-foreground">{point.label}</div>
                    <div className="mt-4 space-y-3">
                      <div>
                        <div className="mb-1 flex justify-between text-xs text-muted-foreground">
                          <span>상승</span>
                          <span>{Math.round(point.bullish * 100)}%</span>
                        </div>
                        <div className="h-2 rounded-full bg-white/8">
                          <div className="h-full rounded-full bg-cyan-400" style={{ width: `${point.bullish * 100}%` }} />
                        </div>
                      </div>
                      <div>
                        <div className="mb-1 flex justify-between text-xs text-muted-foreground">
                          <span>중립</span>
                          <span>{Math.round(point.neutral * 100)}%</span>
                        </div>
                        <div className="h-2 rounded-full bg-white/8">
                          <div className="h-full rounded-full bg-amber-400" style={{ width: `${point.neutral * 100}%` }} />
                        </div>
                      </div>
                      <div>
                        <div className="mb-1 flex justify-between text-xs text-muted-foreground">
                          <span>하락</span>
                          <span>{Math.round(point.bearish * 100)}%</span>
                        </div>
                        <div className="h-2 rounded-full bg-white/8">
                          <div className="h-full rounded-full bg-rose-400" style={{ width: `${point.bearish * 100}%` }} />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    );
  } catch {
    notFound();
  }
}
