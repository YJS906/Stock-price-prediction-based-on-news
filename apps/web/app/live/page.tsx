import { NewsStream } from "@/components/dashboard/news-stream";
import { SectionHeading } from "@/components/dashboard/section-heading";
import { getLiveArticles, getThemes } from "@/lib/api";

export default async function LivePage() {
  const [feed, themes] = await Promise.all([getLiveArticles(undefined, 40), getThemes()]);

  return (
    <section className="space-y-6">
      <SectionHeading
        eyebrow="Live Feed"
        title="실시간 뉴스 전용 페이지"
        description="종목 추천보다 지금 막 올라오는 기사 자체를 우선 보여주는 화면입니다. 최신 발행시각 기준으로 정렬되며, 페이지를 보고 있는 동안 새 뉴스가 자동으로 상단에 추가됩니다."
      />
      <NewsStream
        items={feed.items}
        themeOptions={themes.map((theme) => ({ slug: theme.slug, name: theme.name }))}
        title="전체 실시간 뉴스"
        description="현재 구조에서는 서버 부담과 재연결 안정성을 고려해 SSE 대신 짧은 주기 polling을 사용합니다. 연결이 흔들려도 자동 재시도하며, 새 뉴스는 강조 표시됩니다."
        limit={40}
        density="dense"
        initialGeneratedAt={feed.generatedAt}
        initialContentMode={feed.contentMode}
      />
    </section>
  );
}
