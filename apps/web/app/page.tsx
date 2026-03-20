import Link from "next/link";
import { ArrowRight, Radar } from "lucide-react";

import { ClusterStrip } from "@/components/dashboard/cluster-strip";
import { MarketSummary } from "@/components/dashboard/market-summary";
import { NewsStream } from "@/components/dashboard/news-stream";
import { RankingTable } from "@/components/dashboard/ranking-table";
import { SectionHeading } from "@/components/dashboard/section-heading";
import { ThemeGrid } from "@/components/dashboard/theme-grid";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { getDashboard } from "@/lib/api";

export default async function DashboardPage() {
  const dashboard = await getDashboard();

  return (
    <div className="space-y-8">
      <Card className="overflow-hidden">
        <CardContent className="relative px-6 py-8 lg:px-8 lg:py-10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.16),transparent_22%),radial-gradient(circle_at_bottom_left,rgba(245,158,11,0.12),transparent_22%)]" />
          <div className="relative grid gap-8 lg:grid-cols-[1.4fr_0.9fr]">
            <div className="space-y-5">
              <Badge variant="info">Production-grade MVP · Mock-first</Badge>
              <div className="space-y-3">
                <h1 className="max-w-3xl font-[var(--font-display)] text-4xl font-semibold tracking-tight text-white lg:text-6xl">
                  뉴스에서 끝내지 않고, 테마와 종목 연결까지 압축하는 한국 주식 대시보드
                </h1>
                <p className="max-w-2xl text-sm leading-7 text-slate-300 lg:text-base">
                  국내·해외 뉴스를 필터링하고, 투자 테마로 묶고, 연결된 한국 종목을 랭킹한 뒤 확률형 단기 전망과
                  설명 가능한 근거를 함께 보여줍니다.
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Link href="/themes">
                  <Button>
                    실시간 테마 보기
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/admin/ops">
                  <Button variant="ghost">파이프라인 상태</Button>
                </Link>
              </div>
            </div>

            <div className="grid gap-4">
              <div className="rounded-3xl border border-cyan-400/20 bg-cyan-400/[0.07] p-5">
                <div className="flex items-center gap-3 text-cyan-100">
                  <Radar className="h-5 w-5" />
                  <span className="text-sm uppercase tracking-[0.28em]">Signal Snapshot</span>
                </div>
                <div className="mt-4 text-5xl font-semibold text-white">
                  {((dashboard.topThemes[0]?.momentumScore ?? 0) * 100).toFixed(0)}
                </div>
                <p className="mt-2 text-sm text-cyan-50/80">
                  현재 가장 강한 테마는 <strong>{dashboard.topThemes[0]?.name}</strong> 입니다.
                </p>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                {dashboard.featuredRanking.slice(0, 2).map((item) => (
                  <div key={item.ticker} className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
                    <p className="text-xs uppercase tracking-[0.28em] text-muted-foreground">Top Pick</p>
                    <div className="mt-3 text-2xl font-semibold text-white">{item.nameKo}</div>
                    <p className="mt-2 text-sm text-muted-foreground">{item.thesis}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <MarketSummary cards={dashboard.marketSummary} />

      <section>
        <SectionHeading
          eyebrow="Theme Radar"
          title="실시간 테마 패널"
          description="기사량, 연결 강도, 테마 서사를 기준으로 우선순위를 압축했습니다."
          action={
            <Link href="/themes">
              <Button variant="ghost">전체 테마</Button>
            </Link>
          }
        />
        <ThemeGrid themes={dashboard.topThemes} />
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
        <section>
          <SectionHeading eyebrow="Ranked" title="상위 수혜 종목" description="상승 잠재 관련성 점수를 기준으로 정렬했습니다." />
          <RankingTable items={dashboard.featuredRanking} />
        </section>
        <section>
          <SectionHeading eyebrow="News Flow" title="중요 뉴스 스트림" description="주식 관련성 필터를 통과한 기사만 노출합니다." />
          <NewsStream items={dashboard.latestNews} />
        </section>
      </div>

      <section>
        <SectionHeading eyebrow="Clusters" title="핫 뉴스 클러스터" description="같은 서사로 묶이는 기사 흐름을 빠르게 파악합니다." />
        <ClusterStrip clusters={dashboard.hotClusters} />
      </section>
    </div>
  );
}
