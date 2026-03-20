import Link from "next/link";
import { formatDateTime } from "@newsalpha/shared";

import { SectionHeading } from "@/components/dashboard/section-heading";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getArticles } from "@/lib/api";

export default async function ArticlesPage() {
  const articles = await getArticles();

  return (
    <section className="space-y-6">
      <SectionHeading eyebrow="Filtered Feed" title="주식 관련 뉴스 피드" description="주식과 무관한 사회/연예/사건성 기사는 제거한 흐름입니다." />
      <div className="grid gap-4">
        {articles.map((article) => (
          <Link key={article.id} href={`/articles/${article.id}`}>
            <Card className="transition hover:border-cyan-400/30">
              <CardHeader>
                <div className="flex flex-wrap gap-2">
                  <Badge variant={article.sourceType === "foreign" ? "warning" : "default"}>
                    {article.sourceType === "foreign" ? "해외" : "국내"}
                  </Badge>
                  {article.themes.map((theme) => (
                    <Badge key={`${article.id}-${theme}`} variant="info">
                      {theme}
                    </Badge>
                  ))}
                </div>
                <CardTitle>{article.title}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm leading-6 text-muted-foreground">{article.translatedSummaryKo ?? article.summary}</p>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>
                    {article.sourceName} · {formatDateTime(article.publishedAt)}
                  </span>
                  <span>중요도 {article.importanceLabel}</span>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </section>
  );
}

