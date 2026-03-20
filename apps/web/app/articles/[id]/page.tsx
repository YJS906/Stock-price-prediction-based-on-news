import Link from "next/link";
import { notFound } from "next/navigation";
import { ExternalLink } from "lucide-react";
import { formatDateTime } from "@newsalpha/shared";

import { RankingTable } from "@/components/dashboard/ranking-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getArticle } from "@/lib/api";

export default async function ArticleDetailPage({ params }: { params: { id: string } }) {
  try {
    const article = await getArticle(params.id);

    return (
      <div className="space-y-8">
        <Card>
          <CardContent className="space-y-5 px-6 py-8 lg:px-8">
            <div className="flex flex-wrap gap-2">
              <Badge variant={article.sourceType === "foreign" ? "warning" : "default"}>
                {article.sourceType === "foreign" ? "해외 뉴스" : "국내 뉴스"}
              </Badge>
              {article.themes.map((theme) => (
                <Badge key={theme.id} variant="info">
                  {theme.name}
                </Badge>
              ))}
            </div>
            <div>
              <h1 className="max-w-4xl text-4xl font-semibold text-white">{article.title}</h1>
              <p className="mt-3 text-sm text-muted-foreground">
                {article.sourceName} · {formatDateTime(article.publishedAt)}
              </p>
            </div>
            <p className="max-w-4xl text-sm leading-7 text-slate-200">{article.translatedSummaryKo ?? article.summary}</p>
            <div className="flex flex-wrap gap-3">
              <Link href={article.url} target="_blank">
                <Button>
                  원문 열기
                  <ExternalLink className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              {article.cluster ? <Badge>{article.cluster.headline}</Badge> : null}
            </div>
          </CardContent>
        </Card>

        {article.foreignImpact ? (
          <Card>
            <CardHeader>
              <CardTitle>해외 뉴스의 국내 영향 해석</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-5 lg:grid-cols-2">
              <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
                <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">한국어 번역 요약</p>
                <p className="mt-3 text-sm leading-7 text-slate-200">{article.foreignImpact.translatedSummaryKo}</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
                <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">국내 파급 해석</p>
                <p className="mt-3 text-sm leading-7 text-slate-200">{article.foreignImpact.koreaImpactSummary}</p>
              </div>
            </CardContent>
          </Card>
        ) : null}

        <RankingTable items={article.linkedStocks} title="이 기사와 가장 관련성이 높은 종목" />
      </div>
    );
  } catch {
    notFound();
  }
}

