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
import { BRAND_NAME } from "@/lib/brand";
import { getDashboard } from "@/lib/api";

export default async function DashboardPage() {
  const dashboard = await getDashboard().catch(() => ({
    generatedAt: new Date().toISOString(),
    marketSummary: [],
    topThemes: [],
    latestNews: [],
    featuredRanking: [],
    hotClusters: []
  }));

  return (
    <div className="space-y-8">
      <Card className="overflow-hidden">
        <CardContent className="relative px-6 py-8 lg:px-8 lg:py-10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.16),transparent_22%),radial-gradient(circle_at_bottom_left,rgba(245,158,11,0.12),transparent_22%)]" />
          <div className="relative grid gap-8 lg:grid-cols-[1.3fr_0.95fr]">
            <div className="space-y-5">
              <Badge variant="info">{BRAND_NAME} 실시간 뉴스 대시보드</Badge>
              <div className="space-y-3">
                <h1 className="max-w-3xl font-[var(--font-display)] text-4xl font-semibold tracking-tight text-white lg:text-6xl">
                  뉴스에서 테마를 보고, 종목과 차트까지 이어보는 한국 주식 대시보드
                </h1>
                <p className="max-w-2xl text-sm leading-7 text-slate-300 lg:text-base">
                  국내·해외 뉴스를 주식 관련 기사 중심으로 걸러 실시간 피드로 보여주고, 연관 종목·차트·예측 밴드와 설명 카드를 함께 제공합니다.
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Link href="/live">
                  <Button>
                    실시간 뉴스 보기
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/stocks">
                  <Button variant="ghost">종목 검색</Button>
                </Link>
              </div>
            </div>

            <div className="grid gap-4">
              <div className="rounded-3xl border border-cyan-400/20 bg-cyan-400/[0.07] p-5">
                <div className="flex items-center gap-3 text-cyan-100">
                  <Radar className="h-5 w-5" />
                  <span className="text-sm uppercase tracking-[0.28em]">Live Signal</span>
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

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <section>
          <SectionHeading
            eyebrow="Live Feed"
            title="실시간 주식 뉴스 피드"
            description="가장 최근 기사가 먼저 오고, 새 뉴스는 자동으로 상단에 추가됩니다. 전용 페이지에서는 더 많은 뉴스를 밀도 높게 볼 수 있습니다."
            action={
              <Link href="/live">
                <Button variant="ghost">전체 실시간 뉴스</Button>
              </Link>
            }
          />
          <NewsStream
            items={dashboard.latestNews}
            themeOptions={dashboard.topThemes.map((theme) => ({ slug: theme.slug, name: theme.name }))}
            title="실시간 주식 뉴스"
            description="홈에서는 추천 흐름을 유지하면서도, 실시간 피드 자동 갱신은 계속 유지합니다."
          />
        </section>

        <section>
          <SectionHeading
            eyebrow="Ranking"
            title="상위 반응 가능 종목"
            description="뉴스·테마 연결 강도와 과거 유사 반응을 바탕으로 추린 15개 종목입니다."
          />
          <RankingTable items={dashboard.featuredRanking} />
        </section>
      </div>

      <section>
        <SectionHeading
          eyebrow="Theme Radar"
          title="실시간 테마 흐름"
          description="기사 수와 연결 강도를 기준으로 지금 시장에서 존재감이 큰 테마를 모았습니다."
          action={
            <Link href="/themes">
              <Button variant="ghost">전체 테마</Button>
            </Link>
          }
        />
        <ThemeGrid themes={dashboard.topThemes} />
      </section>

      <section>
        <SectionHeading
          eyebrow="Clusters"
          title="주요 뉴스 클러스터"
          description="같은 이슈로 묶인 기사를 빠르게 비교할 수 있습니다."
        />
        <ClusterStrip clusters={dashboard.hotClusters} />
      </section>
    </div>
  );
}
