import Link from "next/link";
import { type ThemeCard } from "@newsalpha/shared";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ThemeGrid({ themes }: { themes: ThemeCard[] }) {
  return (
    <div className="grid gap-4 xl:grid-cols-3">
      {themes.map((theme) => (
        <Link key={theme.id} href={`/themes/${theme.slug}`}>
          <Card className="h-full transition hover:-translate-y-1 hover:border-cyan-400/30">
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <Badge variant="info">{theme.confidenceLabel}</Badge>
                <span className="text-sm text-cyan-200">{(theme.momentumScore * 100).toFixed(0)}점</span>
              </div>
              <CardTitle>{theme.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm leading-6 text-muted-foreground">{theme.description}</p>
              <div className="flex items-center justify-between text-sm">
                <span className="text-white/80">관련 기사 {theme.articleCount}건</span>
                <span className="text-muted-foreground">모멘텀 중심 보기</span>
              </div>
              <p className="rounded-2xl border border-white/8 bg-white/5 p-3 text-sm text-white/82">{theme.leadNarrative}</p>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}

