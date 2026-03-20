"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";
import { type ForecastWidget } from "@newsalpha/shared";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

export function ForecastChart({ forecast }: { forecast: ForecastWidget }) {
  const option = useMemo(
    () => ({
      backgroundColor: "transparent",
      grid: { left: 8, right: 8, top: 16, bottom: 8, containLabel: true },
      xAxis: {
        type: "value",
        max: 1,
        axisLabel: {
          color: "#94a3b8",
          formatter: (value: number) => `${Math.round(value * 100)}%`
        },
        splitLine: { lineStyle: { color: "rgba(148,163,184,0.10)" } }
      },
      yAxis: {
        type: "category",
        data: ["상승", "보합", "하락"],
        axisLabel: { color: "#e2e8f0" }
      },
      series: [
        {
          type: "bar",
          data: [
            { value: forecast.upProb, itemStyle: { color: "#22d3ee" } },
            { value: forecast.flatProb, itemStyle: { color: "#f59e0b" } },
            { value: forecast.downProb, itemStyle: { color: "#fb7185" } }
          ],
          label: {
            show: true,
            position: "right",
            color: "#f8fafc",
            formatter: ({ value }: { value: number }) => `${Math.round(value * 100)}%`
          },
          barWidth: 16,
          borderRadius: 999
        }
      ]
    }),
    [forecast]
  );

  return <ReactECharts option={option} style={{ height: 180, width: "100%" }} />;
}
