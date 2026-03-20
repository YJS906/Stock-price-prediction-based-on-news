import { SectionHeading } from "@/components/dashboard/section-heading";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getEvaluations } from "@/lib/api";

export default async function EvaluationsPage() {
  const reports = await getEvaluations();

  return (
    <div className="space-y-8">
      <SectionHeading
        eyebrow="Internal Review"
        title="모델 평가 리포트"
        description="모듈별 baseline 성능과 향후 교체 지점을 내부 검토용으로 제공합니다."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        {reports.map((report) => (
          <Card key={report.modelName}>
            <CardHeader>
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="info">{report.modelName}</Badge>
                <Badge>{report.version}</Badge>
              </div>
              <CardTitle>{report.summary}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {report.metrics.map((metric) => (
                <div key={`${report.modelName}-${metric.label}`} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">{metric.label}</span>
                    <span className="text-lg font-semibold text-white">{metric.value}</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-300">{metric.note}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

