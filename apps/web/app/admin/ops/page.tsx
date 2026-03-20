import { PipelineActions } from "@/components/admin/pipeline-actions";
import { SectionHeading } from "@/components/dashboard/section-heading";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getPipelineStatus } from "@/lib/api";

export default async function OpsPage() {
  const status = await getPipelineStatus();

  return (
    <div className="space-y-8">
      <SectionHeading
        eyebrow="Admin / Ops"
        title="파이프라인 상태"
        description="수집기, 필터링 비율, 저장 상태를 내부 운영 화면에서 확인합니다."
        action={<PipelineActions />}
      />

      <div className="data-grid">
        <Card>
          <CardHeader>
            <CardTitle>마지막 인제스트</CardTitle>
          </CardHeader>
          <CardContent>{status.lastIngestedAt}</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>총 기사</CardTitle>
          </CardHeader>
          <CardContent>{status.articlesStored}</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>관련성 비율</CardTitle>
          </CardHeader>
          <CardContent>{Math.round(status.stockRelevantRate * 100)}%</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>워커 상태</CardTitle>
          </CardHeader>
          <CardContent>{status.workerStatus}</CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Provider 상태</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 lg:grid-cols-2">
          {status.providers.map((provider) => (
            <div key={provider.name} className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
              <h3 className="text-lg font-medium text-white">{provider.name}</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {provider.kind} · {provider.status}
              </p>
              <p className="mt-3 text-sm text-slate-200">{provider.lastFetchedAt}</p>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

