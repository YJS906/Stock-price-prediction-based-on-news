import Link from "next/link";
import { formatPercent, formatWon, type RankingEntry } from "@newsalpha/shared";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function RankingTable({ items, title = "상위 수혜 종목" }: { items: RankingEntry[]; title?: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
            <tr>
              <th className="pb-3">종목</th>
              <th className="pb-3">현재가</th>
              <th className="pb-3">당일</th>
              <th className="pb-3">상승 잠재</th>
              <th className="pb-3">근거</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/6">
            {items.map((item, index) => (
              <tr key={item.ticker} className="align-top">
                <td className="py-4">
                  <Link href={`/stocks/${item.ticker}`} className="font-medium text-white hover:text-cyan-200">
                    {index + 1}. {item.nameKo}
                  </Link>
                  <div className="mt-1 text-xs text-muted-foreground">
                    {item.ticker} · {item.market} · {item.sector}
                  </div>
                </td>
                <td className="py-4 text-white/88">{formatWon(item.currentPrice)}</td>
                <td className={`py-4 ${item.dayChangePct >= 0 ? "text-emerald-300" : "text-rose-300"}`}>
                  {formatPercent(item.dayChangePct)}
                </td>
                <td className="py-4">
                  <div className="font-medium text-cyan-200">{(item.upsideScore * 100).toFixed(0)}점</div>
                  <div className="mt-1 h-2 w-24 overflow-hidden rounded-full bg-white/8">
                    <div className="h-full rounded-full bg-cyan-400" style={{ width: `${item.upsideScore * 100}%` }} />
                  </div>
                </td>
                <td className="py-4">
                  <Badge variant="default" className="mb-2">
                    신뢰도 {(item.confidence * 100).toFixed(0)}
                  </Badge>
                  <p className="max-w-sm text-sm leading-6 text-muted-foreground">{item.thesis}</p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}

