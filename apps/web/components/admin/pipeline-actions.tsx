"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.API_BASE_URL ?? "http://localhost:8000";

export function PipelineActions() {
  const [pending, setPending] = useState<null | "ingest" | "reset">(null);
  const [message, setMessage] = useState("운영 액션은 mock ingest를 다시 실행합니다.");

  async function runAction(path: string, mode: "ingest" | "reset") {
    setPending(mode);
    setMessage("작업 실행 중...");
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/${path}`, { method: "POST" });
      const payload = await response.json();
      setMessage(payload.detail ?? "완료");
    } catch {
      setMessage("요청 실패: API 연결 상태를 확인하세요.");
    } finally {
      setPending(null);
    }
  }

  return (
    <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
      <Button disabled={pending !== null} onClick={() => runAction("ingest/run", "ingest")}>
        {pending === "ingest" ? "실행 중..." : "Mock Ingest 실행"}
      </Button>
      <Button variant="ghost" disabled={pending !== null} onClick={() => runAction("seed/reset", "reset")}>
        {pending === "reset" ? "재구성 중..." : "시드 리셋"}
      </Button>
      <p className="text-sm text-muted-foreground">{message}</p>
    </div>
  );
}

