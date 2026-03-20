import { formatDateTime, type ArticleClusterCard } from "@newsalpha/shared";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ClusterStrip({ clusters }: { clusters: ArticleClusterCard[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>핫 뉴스 클러스터</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 lg:grid-cols-3">
        {clusters.map((cluster) => (
          <div key={cluster.id} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
            <div className="mb-3 flex flex-wrap gap-2">
              {cluster.themes.map((theme) => (
                <Badge key={`${cluster.id}-${theme}`} variant="warning">
                  {theme}
                </Badge>
              ))}
            </div>
            <h3 className="text-base font-medium text-white">{cluster.headline}</h3>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">{cluster.summary}</p>
            <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
              <span>기사 {cluster.articleCount}건</span>
              <span>{formatDateTime(cluster.latestPublishedAt)}</span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

