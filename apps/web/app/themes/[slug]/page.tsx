import Link from "next/link";
import { notFound } from "next/navigation";
import { formatDateTime } from "@newsalpha/shared";

import { RankingTable } from "@/components/dashboard/ranking-table";
import { SectionHeading } from "@/components/dashboard/section-heading";
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
            <SectionHeading eyebrow="Ranking" title="테마별 상위 10개 종목" description="관련성·상승 잠재 점수를 합성한 랭킹입니다." />
            <RankingTable items={data.ranking} title={`${data.theme.name} 수혜 랭킹`} />
          </section>
          <section>
            <SectionHeading eyebrow="Clusters" title="주요 클러스터" description="같은 내러티브로 묶이는 기사 흐름입니다." />
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
                      <span>{formatDateTime(cluster.latestPublishedAt)}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>
        </div>

        <section>
          <SectionHeading eyebrow="Articles" title="연결된 최신 뉴스" description="클릭하면 기사 원문 맥락과 연결 종목을 함께 확인할 수 있습니다." />
          <div className="grid gap-4">
            {data.articles.map((article) => (
              <Link
                key={article.id}
                href={`/articles/${article.id}`}
                className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 transition hover:border-cyan-400/30"
              >
                <div className="flex flex-wrap gap-2">
                  {article.themes.map((theme) => (
                    <Badge key={`${article.id}-${theme}`}>{theme}</Badge>
                  ))}
                </div>
                <h3 className="mt-3 text-lg font-medium text-white">{article.title}</h3>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{article.translatedSummaryKo ?? article.summary}</p>
              </Link>
            ))}
          </div>
        </section>
      </div>
    );
  } catch {
    notFound();
  }
}

