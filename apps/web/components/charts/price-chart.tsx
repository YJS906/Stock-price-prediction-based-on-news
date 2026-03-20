"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";
import { type PricePoint } from "@newsalpha/shared";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

export function PriceChart({ data, timeframe = "1m" }: { data: PricePoint[]; timeframe?: string }) {
  const option = useMemo(
    () => ({
      backgroundColor: "transparent",
      animation: false,
      grid: { left: 12, right: 12, top: 24, bottom: 24, containLabel: true },
      tooltip: { trigger: "axis" },
      xAxis: {
        type: "category",
        data: data.map((point) =>
          timeframe === "1d"
            ? new Date(point.time).toLocaleDateString("ko-KR", { month: "2-digit", day: "2-digit" })
            : new Date(point.time).toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" })
        ),
        axisLabel: { color: "#94a3b8" },
        axisLine: { lineStyle: { color: "rgba(148,163,184,0.18)" } }
      },
      yAxis: {
        scale: true,
        axisLabel: { color: "#94a3b8" },
        splitLine: { lineStyle: { color: "rgba(148,163,184,0.10)" } }
      },
      series: [
        {
          type: "candlestick",
          data: data.map((point) => [point.open, point.close, point.low, point.high]),
          itemStyle: {
            color: "#34d399",
            color0: "#fb7185",
            borderColor: "#34d399",
            borderColor0: "#fb7185"
          }
        }
      ]
    }),
    [data, timeframe]
  );

  return <ReactECharts option={option} style={{ height: 360, width: "100%" }} />;
}
