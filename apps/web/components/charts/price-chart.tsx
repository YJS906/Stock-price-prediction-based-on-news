"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";
import { type PricePoint } from "@newsalpha/shared";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

function formatAxisLabel(time: string, timeframe: string) {
  const value = new Date(time);
  if (timeframe === "1m") {
    return value.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" });
  }
  if (timeframe === "1d") {
    return value.toLocaleDateString("ko-KR", { month: "2-digit", day: "2-digit" });
  }
  if (timeframe === "1w") {
    return value.toLocaleDateString("ko-KR", { month: "2-digit", day: "2-digit" });
  }
  return value.toLocaleDateString("ko-KR", { year: "2-digit", month: "2-digit" });
}

export function PriceChart({ data, timeframe = "1d" }: { data: PricePoint[]; timeframe?: string }) {
  const option = useMemo(
    () => ({
      backgroundColor: "transparent",
      animation: false,
      grid: [
        { left: 14, right: 16, top: 18, height: "58%" },
        { left: 14, right: 16, top: "78%", height: "14%" }
      ],
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "cross" }
      },
      xAxis: [
        {
          type: "category",
          data: data.map((point) => formatAxisLabel(point.time, timeframe)),
          scale: true,
          boundaryGap: true,
          axisLine: { lineStyle: { color: "rgba(148,163,184,0.18)" } },
          axisLabel: { color: "#94a3b8" },
          splitLine: { show: false },
          min: "dataMin",
          max: "dataMax"
        },
        {
          type: "category",
          gridIndex: 1,
          data: data.map((point) => formatAxisLabel(point.time, timeframe)),
          scale: true,
          boundaryGap: true,
          axisLine: { lineStyle: { color: "rgba(148,163,184,0.18)" } },
          axisLabel: { show: false },
          splitLine: { show: false },
          min: "dataMin",
          max: "dataMax"
        }
      ],
      yAxis: [
        {
          scale: true,
          axisLabel: { color: "#94a3b8" },
          splitLine: { lineStyle: { color: "rgba(148,163,184,0.10)" } }
        },
        {
          gridIndex: 1,
          axisLabel: {
            color: "#64748b",
            formatter: (value: number) => `${Math.round(value / 1000)}k`
          },
          splitLine: { show: false }
        }
      ],
      series: [
        {
          name: "가격",
          type: "candlestick",
          data: data.map((point) => [point.open, point.close, point.low, point.high]),
          itemStyle: {
            color: "#22c55e",
            color0: "#f43f5e",
            borderColor: "#22c55e",
            borderColor0: "#f43f5e"
          }
        },
        {
          name: "거래량",
          type: "bar",
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: data.map((point) => ({
            value: point.volume,
            itemStyle: {
              color: point.close >= point.open ? "rgba(34,197,94,0.65)" : "rgba(244,63,94,0.65)"
            }
          }))
        }
      ]
    }),
    [data, timeframe]
  );

  if (data.length === 0) {
    return (
      <div className="flex h-[420px] items-center justify-center rounded-3xl border border-dashed border-white/10 bg-white/[0.03] text-sm text-muted-foreground">
        선택한 구간의 차트 데이터가 없습니다.
      </div>
    );
  }

  return <ReactECharts option={option} style={{ height: 420, width: "100%" }} />;
}
