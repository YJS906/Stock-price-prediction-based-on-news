"use client";

import { useState, useTransition } from "react";
import { type PricePoint } from "@newsalpha/shared";

import { PriceChart } from "@/components/charts/price-chart";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getStockChart } from "@/lib/api";

const timeframeLabels: Record<string, string> = {
  "1m": "분봉",
  "1d": "일봉",
  "1w": "주봉",
  "1mo": "월봉"
};

type StockChartPanelProps = {
  ticker: string;
  initialTimeframe: string;
  initialPoints: PricePoint[];
  availableTimeframes: string[];
};

export function StockChartPanel({
  ticker,
  initialTimeframe,
  initialPoints,
  availableTimeframes
}: StockChartPanelProps) {
  const [timeframe, setTimeframe] = useState(initialTimeframe);
  const [points, setPoints] = useState(initialPoints);
  const [isPending, startTransition] = useTransition();

  function handleSelect(nextTimeframe: string) {
    if (nextTimeframe === timeframe) return;

    startTransition(() => {
      void (async () => {
        const response = await getStockChart(ticker, nextTimeframe);
        setTimeframe(response.timeframe);
        setPoints(response.points);
      })();
    });
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          {availableTimeframes.map((item) => (
            <Button
              key={item}
              type="button"
              variant={item === timeframe ? "default" : "ghost"}
              className="h-9 rounded-full"
              onClick={() => handleSelect(item)}
            >
              {timeframeLabels[item] ?? item}
            </Button>
          ))}
        </div>
        <Badge variant="info">{isPending ? "차트 갱신 중" : `${timeframeLabels[timeframe] ?? timeframe} 기준`}</Badge>
      </div>

      <PriceChart data={points} timeframe={timeframe} />
    </div>
  );
}
