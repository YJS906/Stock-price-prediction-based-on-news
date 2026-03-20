import { getDashboard } from "@/lib/api";
import { RankingTable } from "@/components/dashboard/ranking-table";
import { SectionHeading } from "@/components/dashboard/section-heading";

export default async function StocksPage() {
  const dashboard = await getDashboard();

  return (
    <section className="space-y-6">
      <SectionHeading
        eyebrow="Coverage"
        title="현재 집중 관찰 종목"
        description="뉴스 연결 강도와 테마 서사를 기준으로 우선 모니터링해야 할 종목입니다."
      />
      <RankingTable items={dashboard.featuredRanking} title="대시보드 상위 종목" />
    </section>
  );
}

