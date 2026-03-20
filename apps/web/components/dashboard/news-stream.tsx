import Link from "next/link";
import { formatDateTime, type NewsCard } from "@newsalpha/shared";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function NewsStream({ items }: { items: NewsCard[] }) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>최신 중요 뉴스</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {items.map((item) => (
          <Link
            key={item.id}
            href={`/articles/${item.id}`}
            className="block rounded-2xl border border-white/8 bg-white/[0.03] p-4 transition hover:border-cyan-400/30 hover:bg-cyan-400/[0.04]"
          >
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <Badge variant={item.sourceType === "foreign" ? "warning" : "default"}>
                {item.sourceType === "foreign" ? "해외" : "국내"}
              </Badge>
              <Badge variant="info">{item.importanceLabel}</Badge>
              {item.themes.slice(0, 2).map((theme) => (
                <Badge key={`${item.id}-${theme}`}>{theme}</Badge>
              ))}
            </div>
            <h3 className="text-base font-medium leading-6 text-white">{item.title}</h3>
            <p className="mt-2 max-h-12 overflow-hidden text-sm leading-6 text-muted-foreground">
              {item.translatedSummaryKo ?? item.summary}
            </p>
            <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
              <span>
                {item.sourceName} · {formatDateTime(item.publishedAt)}
              </span>
              <span>관련성 {(item.relevanceScore * 100).toFixed(0)}</span>
            </div>
          </Link>
        ))}
      </CardContent>
    </Card>
  );
}
