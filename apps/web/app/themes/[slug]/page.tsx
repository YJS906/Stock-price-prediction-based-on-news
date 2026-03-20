import { notFound } from "next/navigation";

import { RankingTable } from "@/components/dashboard/ranking-table";
import { SectionHeading } from "@/components/dashboard/section-heading";
import { NewsStream } from "@/components/dashboard/news-stream";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getTheme } from "@/lib/api";

export default async function ThemeDetailPage({ params }: { params: { slug: string } }) {
  try {
    const data = await getTheme(params.slug);

    return (
      <div className="space-y-8">
        <Card>
          <CardContent className="grid gap-6 px-6 py-8 lg:grid-cols-[1.4fr_0.9fr] lg:px-8">
            <div className="space-y-4">
              <Badge variant="info">{data.theme.confidenceLabel}</Badge>
              <div>
                <h1 className="text-4xl font-semibold text-white">{data.theme.name}</h1>
                <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">{data.theme.description}</p>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-1">
              <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
                <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Momentum Score</p>
                <div className="mt-3 text-4xl font-semibold text-cyan-200">{(data.theme.momentumScore * 100).toFixed(0)}</div>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
                <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Articles</p>
                <div className="mt-3 text-4xl font-semibold text-white">{data.theme.articleCount}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-6 xl:grid-cols-[1.25fr_0.95fr]">
          <section>
            <SectionHeading eyebrow="Ranking" title="테마별 상위 종목" description="관련성·상승 여지를 합산한 확률형 랭킹입니다." />
            <RankingTable items={data.ranking} title={`${data.theme.name} 상위 종목`} />
          </section>
          <section>
            <SectionHeading eyebrow="Clusters" title="주요 클러스터" description="같은 이슈로 묶이는 기사 흐름입니다." />
            <div className="space-y-4">
              {data.clusters.map((cluster) => (
                <Card key={cluster.id}>
                  <CardHeader>
                    <CardTitle>{cluster.headline}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <p className="text-sm leading-6 text-muted-foreground">{cluster.summary}</p>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>기사 {cluster.articleCount}건</span>
                      <span>{new Intl.DateTimeFormat("ko-KR", { dateStyle: "medium", timeStyle: "short" }).format(new Date(cluster.latestPublishedAt))}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>
        </div>

        <section>
          <SectionHeading
            eyebrow="Articles"
            title={`${data.theme.name} 실시간 뉴스`}
            description="같은 테마의 최신 기사만 자동으로 상단에 추가됩니다."
          />
          <NewsStream
            items={data.articles}
            fixedThemeSlug={params.slug}
            themeOptions={[{ slug: data.theme.slug, name: data.theme.name }]}
            title={`${data.theme.name} 뉴스 피드`}
            description="테마별 최신순 정렬과 자동 갱신을 지원합니다."
            limit={16}
          />
        </section>
      </div>
    );
  } catch {
    notFound();
  }
}
